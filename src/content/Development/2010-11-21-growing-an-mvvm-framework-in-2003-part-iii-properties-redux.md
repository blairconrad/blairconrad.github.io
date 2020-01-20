---
layout: post
title: Growing an MVVM Framework in 2003, part III&mdash;Properties Redux
comments: true
tags: Development, Frameworks, MVVM
---
<div style="padding-left:.5em;padding-right:.5em;margin-left:2em;margin-right:2em;border:1px solid #EEE;background-color:#F8F8F8;">
<p>This post is from a series on my experiences starting to grow an MVVM Framework in .NET 1.1.</p>

* <a href="{filename}2010-10-29-growing-an-mvvm-framework-in-2003-part-i-event-handlers.md">Part I&mdash;Event Handlers</a>
* <a href="{filename}2010-11-10-growing-an-mvvm-framework-in-2003-part-ii-properties.md">Part II &#8211; Properties</a>
* Part III  &#8211; Properties Redux
* <a href="{filename}2010-11-30-growing-an-mvvm-framework-in-2003-part-iv-unit-tests.md">Part IV&mdash;Unit Tests</a>
* <a href="{filename}2011-02-15-growing-an-mvvm-framework-in-2003-part-v-reflections-and-regrets.md">Part V&mdash;Reflections and Regrets</a>

<p>Full source code can be found in my <a href="http://code.google.com/p/blairconrad/source/browse/#svn/trunk/BlogExamples/2010-11-mvvm-.net1.1/BookFinder">Google Code repository</a>.</p>
</div>

<h2>A Change of Plans</h2>
Last time I showed how I managed the binding of ViewModel properties to the properties on the View's controls.  I promised to talk this time about how the use of the mini-framework affected the testability of the code. I changed my mind&mdash;I want to return to the whole properties discussion.

<h2>Festering Dissatisfaction</h2>
The method I had for binding ViewModel properties to the View worked, but it left a bad taste in my mouth. A few things bothered me about the implementation. Recall that to add a bound property the ViewModel had to have code something like this:
<pre><code class="csharp">private Property bookListItems;
public string BookListItems
{
    get { return bookListItems.AsList(); }
    set { bookListItems.Value = value; }
}</code></pre>
I have a couple of problems with this.

<ol>
<li>it's pretty chatty</li>
<li>the client programmer has to know when to use <code>.AsList()</code> or not, since strings and bools don't require it</li>
<li>the viewbinding code had to look for the private field, and that just felt gross</li>
</ol>

<h2>Poor man's generics</h2>
When I first wrote the code, I was bothered a little by the weaknesses in the property bindings. It wasn't until I wrote <i>about</i> the code here that the suck really started to get to me. And worse, I was unhappy with what I'd wrote. One phrase from the post kept coming back to me:

>At this point, I was really missing generics.

What did I mean by that? Why did I miss generics? I hadn't explained that well, even to myself. So I thought about it. What would I do with the generics if I had them? And I thought for a bit longer. Then I had it. I'd make a <code>Property</code> class to proxy the view's properties&mdash;that would tighten up the code and relieve programmers of the burden of knowing when to use `.AsList`.

Well, I don't have generics, but I do have Manual Type Creation. That's somewhat less convenient, but it's not like I'm going to need dozens of different property types&mdash;3 will do for a start.  So I decided to see what I could do with a little Property type hierarchy.

<pre><code class="csharp">public abstract class Property
{
    protected PropertyStorageStrategy storage;

    protected Property(PropertyStorageStrategy storage)
    {
        this.storage = storage;
    }
}

public class ListProperty: Property
{
    public ListProperty(PropertyStorageStrategy storage): base(storage)
    {}

    public IList Value
    {
        get { return (IList) storage.Get(); }
        set { storage.Set(value); }
    }
}

public class StringProperty: Property
{
    // pretty much what you'd expect
}

public class BoolProperty: Property
{
    // pretty much what you expected above, only more Bool-y
}</code></pre>

There's not a terrible amount here, just a family of properties. Each concrete class is responsible for providing a <code>Value</code> property that will return (or accept) a typed value. The real work is done by the <code>storage</code> member&mdash;it keeps track of the untyped value that the concrete class will take or dole out. As the name <code>PropertyStorageStrategy</code> suggests, a Property can vary the source and sink for its value via the  <a href="http://en.wikipedia.org/wiki/Strategy_pattern">Strategy design pattern</a>. 

<h2>I was holding it for a friend</h2>
Let's look at the storage strategy that defers to a property on another object.
<pre><code class="csharp"> public interface PropertyStorageStrategy
 {
     object Get();
     void Set(object value);
 }

public class BoundPropertyStrategy: PropertyStorageStrategy 
{
      private object obj;
      private PropertyInfo propertyInfo;

      public BoundPropertyStrategy(object obj, PropertyInfo property)
      {
         this.obj = obj;
         this.propertyInfo = property;
      }

      public void Set(object value)
      {
         propertyInfo.SetValue(obj, value, null);
      }

      public object Get()
      {
         return propertyInfo.GetValue(obj, null); 
      }
}</code></pre>

Unsurprisingly, this looks a lot like the <code>BoundProperty</code> class from last time. After all, the core functionality is pretty much the same. So, inject a BoundProperty into one of ListProperty, StringProperty, or BoolProperty, and we get a strongly-typed proxy for the underlying object.

<h2>Tying it together</h2>
Of course the new classes required a change to the ViewModel/Model binding code. Locating the ViewModel fields to bind is pretty much the same as it was, except only public fields that derive from Property are considered. The BindFieldToControl becomes the slightly-better named <code>BindPropertyToControl</code>:
<pre><code class="csharp linenos=table">private bool BindPropertyToControl(Control control, FieldInfo field)
{
    string controlPropertyName = ControlAttributeName(control, field.Name);
    if ( controlPropertyName == null )
    {
        return false;
    }

    PropertyInfo controlProperty = control.GetType().GetProperty(controlPropertyName, myBindingFlags);
    if ( controlProperty == null )
    {
        return false;
    }
     
    BoundPropertyStrategy strategy = new BoundPropertyStrategy(control, controlProperty);
    ConstructorInfo constructor = field.FieldType.GetConstructor(new Type[] {typeof (PropertyStorageStrategy)});
    object propertyField = constructor.Invoke(new object[] {strategy});
    field.SetValue(this, propertyField);
    return true;
}</code></pre>

The first part of the method just makes sure that the control we've found has a name that matches the first part of the property. Then we look for a property on the control that completes the name. Once those hurdles are past, the magic happens:

<ol start="15">
  <li>create a new BoundProperty to proxy the control's property value</li>
  <li>take the property field type and find the constructor that takes a PropertyStorageStrategy</li>
  <li>make a new property object, passing in our BoundProperty</li>
  <li>set the property object onto the ViewModel</li>
</ol>

<h2>How's it work?</h2>
Overall, I think okay. Here's a sample of the ViewModel code.
<pre><code class="csharp">public StringProperty TitleText;
public BoolProperty FindEnabled;
public ListProperty BookListItems;

public void TitleTextChanged(object sender, EventArgs e)
{
    string newText = TitleText.Value;
    FindEnabled.Value = (newText != null &amp; newText.Length &gt; 0);
}

public void FindClick(object sender, EventArgs e)
{
    ICollection books = bookDepository.Find(TitleText.Value);
    IList bookListItems = BookListItems.Value;

    bookListItems.Clear();
    foreach ( string book in books )
    {
        bookListItems.Add(book);
    }
}</code></pre>

The client developer has to remember to use the funny property types,
but this isn't that much harder than, say `Func`. At least the names
make some sense.  The `.Value` could get a little old, but I prefer
having it on both the get and the set even over just on the set. I
like having the strong-typing built in to the type, rather than
forcing the client developer to do the conversion in a property.

On the downside, additional property types will have to be added to
the framework by hand, but that shouldn't come up too often. Also, the
storage strategy for the properties is maybe a little complicated, but
at least clients of the framework never have to deal with it
directly. The observant among you will probably criticize the strategy
because so far there's no use for it. Bear with me. Next time I'll
show you how the strategy adds value.

