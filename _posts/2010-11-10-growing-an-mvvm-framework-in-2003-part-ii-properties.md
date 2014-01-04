---
layout: post
title: Growing an MVVM Framework in 2003, part II&mdash;Properties
tags:
    - Development
    - Frameworks
    - MVVM
---
<div style="padding-left:.5em;padding-right:.5em;margin-left:2em;margin-right:2em;border:1px solid #EEE;background-color:#F8F8F8;">

<p>This is second post in a series on my experiences starting to grow an MVVM Framework in .NET 1.1.</p>

* <a href="{{ site.url }}{% post_url 2010-10-29-growing-an-mvvm-framework-in-2003-part-i-event-handlers %}">Part I&mdash;Event Handlers</a>
* Part II&mdash;Properties
* <a href="{{ site.url }}{% post_url 2010-11-21-growing-an-mvvm-framework-in-2003-part-iii-properties-redux %}">Part III &mdash;Properties Redux
* <a href="{{ site.url }}{% post_url 2010-11-30-growing-an-mvvm-framework-in-2003-part-iv-unit-tests %}">Part IV&mdash;Unit Tests</a>
* <a href="{{ site.url }}{% post_url 2011-02-15-growing-an-mvvm-framework-in-2003-part-v-reflections-and-regrets %}">Part V&mdash;Reflections and Regrets</a>

Full source code can be found in my <a href="http://code.google.com/p/blairconrad/source/browse/#svn/trunk/BlogExamples/2010-10-mvvm-.net1.1/BookFinder">Google Code repository</a>.

</div>

Last time, I introduced a tiny Windows Forms application and described my efforts to make a small MVVM framework for it. At the end of that post, we'd seen one way to use convention to bind View events to ViewModel event handlers.

Today I'll talk about properties. It's all very well to have a click on the "Find" button trigger the FindClick method on the ViewModel, but it's useless unless we know <em>what to look for</em>. I needed a way to pass the <code>Title.Text</code> value to the ViewModel so it could use it for the search.
 Then the FindClick method I showed last time would work:
{% highlight csharp %}
public void FindClick(object sender, EventArgs e)
{
    ICollection books = bookDepository.Find(TitleText);
    BookListItems.Clear();
    foreach ( string book in books )
    {
        BookListItems.Add(book);
    }
}
{% endhighlight %}

<h2>A Failed Attempt</h2>
First I tried using Windows Forms binding, with lamentable results. I wish I'd saved the intermediate steps, as I was probably doing something wrong and could've solicited help. Still, whether it was due to a lack of experience on my part, or a flaw in the system, the bindings just wouldn't work. I could bind bools and strings, but lists were right out. 

<h2>A Proxy for Properties</h2>
I decided to rely on the storage objects that came with the View elements. This meant the ViewModel needed some way to proxy the properties on the View. Then a get or a set on the ViewModel object would flow right through, reading or writing the View's values.
Here's what I came up with:
{% highlight csharp %}
public class BoundProperty: Property
{
    private object obj;
    private PropertyInfo propertyInfo;

    public BoundProperty(object obj, PropertyInfo property)
    {
        this.obj = obj;
        this.propertyInfo = property;
    }

    public override object Value
    {
        get { return propertyInfo.GetValue(obj, null); }
        set { propertyInfo.SetValue(obj, value, null); }
    }
}
{% endhighlight %}
Ignore the <code>Property</code> base class for a bit. An instances <code>p</code> of type <code>BoundProperty</code> can be used to get and set values on the proxied object <code>obj</code> like so:
{% highlight csharp %}
p.Value = valueA;
object valueB = p.Value;
{% endhighlight %}

Not incredibly thrilling, but one can work with it. Using the <code>.Value</code> in order to access the value was a little cumbersome, so I added a little syntactic sugar in the Property base class:
{% highlight csharp %}
public abstract class Property
{
    public abstract object Value { get; set; }

    public static implicit operator string(Property prop)
    {
        return (string) prop.Value;
    }

    public static implicit operator bool(Property prop)
    {
        return (bool) prop.Value;
    }

    public IList AsList()
    {
         return (IList) Value;
    } 
}
{% endhighlight %}


I really like the implicit operator functionality, which I'd never used before. I wish it could be used with interfaces, though. There's probably a good reason why it can't, but nothing comes to mind. Anyhow, I had to go another route for IList&mdash;the somewhat uninspiring <code>AsList</code> method. At this point, I was really missing generics.

Still, it's nicer to be able to write
{% highlight csharp %}
string myString = p1;
IList myList = p2.AsList();
{% endhighlight %}
instead of 
{% highlight csharp %}
string myString = (string) p1.Value;
IList myList = (IList) p2.Value;
{% endhighlight %}

<h2>Hooking up the Properties</h2>
This is pretty much the same as hooking up the events like the last time. All we have to do is define a field (yes, a field) of type Property in the ViewModel:
{% highlight csharp %}
private Property titleText;
{% endhighlight %}

The ViewModelBase loops over all the Property fields and looks for View controls that have matching property names:
{% highlight csharp %}
foreach ( FieldInfo field in PropertyFields() )
{
    FindPropertyToBindTo(allControls, field);
}

private void FindPropertyToBindTo(ArrayList allControls, FieldInfo field)
{
    foreach ( Control control in allControls )
    {
        if ( BindFieldToControl(control, field) ) { return; }
    }
}

private bool BindFieldToControl(Control control, FieldInfo field)
{
    string controlPropertyName = ControlAttributeName(control, field);
    if ( controlPropertyName == null ) { return false; }

    PropertyInfo controlProperty = control.GetType().GetProperty(controlPropertyName, myBindingFlags);
    if ( controlProperty != null )
    {
        field.SetValue(this, new BoundProperty(control, controlProperty));
    }
    return true;
}
{% endhighlight %}

Technically that's it, but the rest of the ViewModel's code is a little cleaner if we <a href="http://www.refactoring.com/catalog/selfEncapsulateField.html">self encapsulate the field</a>:

{% highlight csharp %}
public string TitleText
{
    get { return titleText; }
    set { titleText.Value = value; }
}
{% endhighlight %}

<h2>Remarks</h2>
Once the infrastructure was in place, I really started enjoying developing the application. It was very liberating to add a new event handler just by writing a method with the right name and signature. And even adding access to a new property wasn't so bad&mdash;writing the three lines of code to segregate the conversions and <code>.Value</code>s was worth it to keep the event handler bodies nice and clean.

Next time, we'll see how the design affected the form of the application's unit tests.



