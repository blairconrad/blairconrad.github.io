---
layout: post
title: Growing an MVVM Framework in 2003, part IV&mdash;Unit Tests
comments: true
tags: .NET, Frameworks, MVVM, Testing
---
<div style="padding-left:.5em;padding-right:.5em;margin-left:2em;margin-right:2em;border:1px solid #EEE;background-color:#F8F8F8;">
<p>This post is from a series on my experiences starting to grow an MVVM Framework in .NET 1.1.</p>

* <a href="{filename}../2010\/10-29-growing-an-mvvm-framework-in-2003-part-i-event-handlers.md">Part I&mdash;Event Handlers</a>
* <a href="{filename}../2010\/11-10-growing-an-mvvm-framework-in-2003-part-ii-properties.md">Part II&mdash;Properties</a>
* <a href="{filename}../2010\/11-21-growing-an-mvvm-framework-in-2003-part-iii-properties-redux.md">Part III &mdash;Properties Redux</a>
* Part IV&mdash;Unit Tests
* <a href="{filename}../2011\/02-15-growing-an-mvvm-framework-in-2003-part-v-reflections-and-regrets.md">Part V&mdash;Reflections and Regrets</a>

<p>Full source code can be found in my <a href="http://code.google.com/p/blairconrad/source/browse/#svn/trunk/BlogExamples/2010-11-mvvm-.net1.1/BookFinder">Google Code repository</a>.</p>
</div>

In parts 1 and 3 (and 2, but I like part 3 better) I showed a tiny "framework" for binding View properties and events to properties and methods on a ViewModel. In addition to avoiding the tedium and noise of wiring up events by hand, I'd hoped to implement a structure that would make unit testing easier. Let's see how that went.

<h2>Event handlers just work. Almost</h2>
Recall that event handlers are defined on the ViewModel as plain old methods that happen to take a specific set of arguments&mdash;usually <code>object</code> and something that derives from <code>EventArgs</code>. This means that nothing special has to be done in order to exercise the methods during a unit test. The test doesn't have to trick the ViewModel into registering with an event or anything. The test just calls the method. And if the method doesn't care much about its arguments like <code>FindClick</code> doesn't, you can pass in nonsense:
<pre><code class="csharp">public class BookListViewModel
{
    public void FindClick(object sender, EventArgs e)
    {
        ICollection books = bookDepository.Find(TitleText.Value);
        IList bookListItems = BookListItems.Value;

        bookListItems.Clear();
        foreach ( string book in books )
        {
             bookListItems.Add(book);
        }
    }
}

public class BookListViewModelTests
{
    [Test]
    public void CallFindClick()
    {
        vm.FindClick(null, null);
    }
}</code></pre>

Of course, this isn't much of a test. Usually we'll want to set up some initial state for the ViewModel, and verify that the correct actions have been taken. In fact, as things stand, the property fields will all be null, so <code>TitleText.Value</code> and <code>BookListItems.Value</code> will error out.

<h2>Putting something behind the properties</h2>
Most event handlers will need to access the properties on the ViewModel, so the tests must hook up the properties.

<h3>Provide stub properties</h3>
Last time I mentioned that the <code>PropertyStorageStrategy</code> would bring value. This is it. Recall the definitions of the ListProperty and the PropertyStorageStrategy:

<pre><code class="csharp">public class ListProperty: Property
{
    public ListProperty(PropertyStorageStrategy storage): base(storage)
    {}

    public IList Value
    {
        get { return (IList) storage.Get(); }
        set { storage.Set(value); }
    }
}

 public interface PropertyStorageStrategy
 {
     object Get();
     void Set(object value);
 }</code></pre>

The ListProperty (and BoolProperty and StringProperty) merely consult a PropertyStorageStrategy to obtain a value and they cast it to the correct type. Providing a dumb strategy that, instead of proxying a property on a View control, just holds a field will produce a property that can be used in tests:

<pre><code class="csharp">public class ValuePropertyStrategy: PropertyStorageStrategy 
{
      private object obj;

      public ValuePropertyStrategy(object initialValue)
      {
         this.obj = initialValue;
      }

      public void Set(object value) { obj = value; }
      public object Get() { return obj; }
}</code></pre>

Then the test fixture setup can bind properties to the ViewModel:
<pre><code class="csharp">[SetUp]
public void SetUp()
{
    vm = new BookListViewModel(new Control(), new FakeBookDepository());
    vm.TitleText = new StringProperty(new ValuePropertyStrategy(""));
    vm.BookListItems = new ListProperty(new ValuePropertyStrategy(new ArrayList()));
    ...
}</code></pre>

And tests can be constructed to provide initial property values (if the default isn't good enough) and interrogate them afterward.
<pre><code class="csharp">[Test]
public void FindClick_WithTitleG_FindsEndersGame()
{
    vm.TitleText.Value = "G";
    vm.FindClick(null, null);

    Assert.IsTrue(vm.BookListItems.Value.Contains("Ender's Game"));
}</code></pre>

<h3>Auto-wiring the properties</h3>

This works, and pretty well. There's not that much noise associated with setting up the fake properties. Still, why should there be any? After so much trouble to remove the tedious wiring up from the production code, it seems wrong to leave it in the testing code.
Also, I'm against <i>anything</i> that adds a barrier to writing tests. And having to hand-wire a few (or a dozen) properties before you can start testing is definitely a barrier. 

So, let's write a little code to handle the tedium for us.

<pre><code class="csharp">public class ValuePropertyBinder
{
      public static void Bind(ViewModelBase viewModel)
      {
          foreach ( FieldInfo field in viewModel.PropertyFields() )
          {
              ValuePropertyStrategy propertyStorageStrategy = new ValuePropertyStrategy(MakeStartingValue(field.FieldType));

              ConstructorInfo propertyConstructor = field.FieldType.GetConstructor(new Type[] {typeof (PropertyStorageStrategy)});
              object propertyField = propertyConstructor.Invoke(new object[] {propertyStorageStrategy});
              field.SetValue(viewModel, propertyField);
          }
      }

      private static object MakeStartingValue(Type fieldType)
      {
         Type propertyType = fieldType.GetProperty("Value").PropertyType;
         
         if ( propertyType == typeof(IList) ) { return new ArrayList(); }
         if ( propertyType == typeof(string) ) { return ""; }
         if ( propertyType == typeof(bool) ) { return false; }
         else
         { 
              throw new NotImplementedException("no known starting value for type " + propertyType);
         }
      }
}</code></pre>

This is very similar to the wiring we've seen before&mdash;find property fields, construct an object to implement the property, and hook it up. The only thing likely to need attention in the future is <code>MakeStartingValue</code>. A new property type(like DateTime), will require an expansion to the <code>if</code> chain. But that should be very infrequent.

Now it's much easier to use the ViewModel in tests:
<pre><code class="csharp">[SetUp]
public void SetUp()
{
   vm = new BookListViewModel(new Control(), new FakeBookDepository());
   ValuePropertyBinder.Bind(vm);
}</code></pre>

<h3>An alternative: brute force and ignorance</h3>
This approach didn't occur to me until the project was over. Sigh.
The production code works by binding the ViewModel to a View. The test setup could do that. I'd taken pains to keep any kind of code or behaviour out of the View, so there shouldn't be any side effects, and there's no need to show any of the GUI elements. Honestly, the technical downsides seem pretty limited.

Even so, I don't <i>like</i> this solution. For the BookFinder application, the View is simple enough that I'm confident the approach would work, but I have concerns over using it in a more complex application. Also, I prefer to reduce the amount of auxiliary production code that's used in tests. In the off chance that something does go wrong, it's nice to be able to have a small set of production code to look at

<h2>Summing up</h2>
With the ValuePropertyBinder (or much-maligned "just bind the ViewModel  to the actual Model"), tests are really easy to set up and run. As easy as writing the production code. And they're readable. The only troublesome dependencies are the models. Totally worth the effort.
