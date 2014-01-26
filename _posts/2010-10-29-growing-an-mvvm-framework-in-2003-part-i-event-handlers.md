---
layout: post
title: Growing an MVVM Framework in 2003, part I&mdash;Event Handlers
comments: true
tags:
    - Development
    - Frameworks
    - MVVM
---

<div style="padding-left:.5em;padding-right:.5em;margin-left:2em;margin-right:2em;border:1px solid #EEE;background-color:#F8F8F8;">

This is one post in a series on my experiences starting to grow an MVVM Framework in .NET 1.1.

* Part I&mdash;Event Handlers
* <a href="{{ site.url }}{% post_url 2010-11-10-growing-an-mvvm-framework-in-2003-part-ii-properties %}">Part II&mdash;Properties</a>
* <a href="{{ site.url }}{% post_url 2010-11-21-growing-an-mvvm-framework-in-2003-part-iii-properties-redux %}">Part III &mdash;Properties Redux
* <a href="{{ site.url }}{% post_url 2010-11-30-growing-an-mvvm-framework-in-2003-part-iv-unit-tests %}">Part IV&mdash;Unit Tests</a>
* <a href="{{ site.url }}{% post_url 2011-02-15-growing-an-mvvm-framework-in-2003-part-v-reflections-and-regrets %}">Part V&mdash;Reflections and Regrets</a>

Full source code can be found in my <a href="http://code.google.com/p/blairconrad/source/browse/#svn/trunk/BlogExamples/2010-10-mvvm-.net1.1/BookFinder">Google Code repository</a>.

</div>

At the Day Job I usually work on web services, but I recently had the opportunity to write a customer-facing tool that had a GUI.

Previously, I <a href="{{ site.url }}{% post_url 2010-04-02-watch-even-if-youre-not-building-an-mvvm-app %}">expressed my excitement over the Rob Eisenberg  "Build Your Own MVVM framework" talk</a>. Ever since, I've been dying to try my hand at an MVVM application. I wanted to create an application that

* had testable logic, even in the GUI layer,
* had no "codebehind" in the view, and
* shunted the tedious wiring up of events and handlers into helpers (or a "framework")

Unfortunately, the application was intended to work at our established customers' sites, so I couldn't depend on WPF, or even .NET 2.0&mdash;it's 1.1 all the way.

<h2>The Goal</h2>
I'll demonstrate with a simpler app than the one from work, but will cover the the relevant concepts. For the purpose of this post, I'll be writing a book-finding app. The user will be able to enter a substring to use to search a database; the matching entries will be displayed in a ListBox and when one of them is selected, some notes will be displayed in a TextBox.

<a href="{{ site.image_dir }}/bookfindermockup.png"><img class="aligncenter size-full wp-image-595" title="bookfindermockup" src="{{ site.image_dir }}/bookfindermockup.png" alt="BookFinder Mockup" width="480" height="337" /></a>

I didn't want to have to riddle my ViewModel with <code>+=</code>s just to be able to react to button presses and item selections from the view. I wanted to write something like:

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
and have the method run when the <code>Click</code> event on the <code>Find</code> button was raised. The method should use the value of the <code>Text</code> property of the <code>Title</code> TextBox to find a list of books and put them in the <code>Items</code> collection on the <code>BookList</code> ListBox.

<h2>Wiring up Event Handlers</h2>
I created a ViewModelBase class to handle all the infrastructure, so the BookListViewModel code could focus on app-related functions. The first thing <code>ViewModelBase.BindToView</code> does is seek out event handlers to bind to on the supplied View (which can be any Controller object):
 
{% highlight csharp %}
ArrayList allControls = AllControlsDescendingFrom(View);
foreach ( MethodInfo handler in EventHandlers() )
{
    FindEventToListenTo(allControls, handler);
}
{% endhighlight %}

<code>AllControlsDescendingFrom</code> recursively looks through all the controls rooted at the View and returns them as a flat list. <code>EventHandlers</code> uses reflection to locate public methods on the ViewModel that have event-like signatures:
{% highlight csharp %}
private IEnumerable EventHandlers()
{
    ArrayList eventHandlers = new ArrayList();
    foreach ( MethodInfo method in this.GetType().GetMethods(BindingFlags.Instance | BindingFlags.Public) )
    {
        if ( isEventHandler(method) )
        {
            eventHandlers.Add(method);
        }
    }
    return eventHandlers;
}

private bool isEventHandler(MethodInfo info)
{
    ParameterInfo[] parameters = info.GetParameters();
    return
        (info.ReturnType == typeof (void) &&
         parameters.Length == 2 &&
         parameters[0].ParameterType == typeof(object) &&
         (typeof(EventArgs)).IsAssignableFrom(parameters[1].ParameterType));
}
{% endhighlight %}
Note the last line. I'd originally just checked that the second parameter <em>was of type <code>EventArgs</code></em>. This worked for many event types, like the Click event on a Button and the SelectedIndexChanged event on a ListBox, but failed to match others, such as a TextBox's KeyPress event:
{% highlight csharp %}
public delegate void KeyPressEventHandler(object sender, KeyPressEventArgs e)
{% endhighlight %}

<code>FindEventToListenTo</code> looks through the allControls list. If there's a control with name <em>Controlname</em> and an event <em>Eventname</em>, it will bind to a handler named <em>ControlnameEventname</em>. For example method SearchClick would be hooked up to the Click event on a control called Search.

{% highlight csharp linenos=table %}
private void FindEventToListenTo(ArrayList allControls, MethodInfo handler)
{
    foreach ( Control control in allControls )
    {
        if ( ListenToEvent(control, handler) )
        {
            return;
        }
    }
}

private bool ListenToEvent(Control control, MethodInfo method)
{
    string eventName = ControlAttributeName(control, method);
    if ( eventName == null )
    {
        return false;
    }
    
    EventInfo eventInfo = control.GetType().GetEvent(eventName, BindingFlags.Instance | BindingFlags.Public);
    if ( eventInfo == null )
    {
        return false;
    }

    eventInfo.GetAddMethod().Invoke(control, new object[]
                  {
                    Delegate.CreateDelegate(eventInfo.EventHandlerType, this, method.Name)
                  });
    return true;
}
{% endhighlight %}

This is pretty straightforward, with two exceptions. Creating the delegate to wrap the ViewModel method was a little tricky&mdash;I had to reference the specific <code>EventHandlerType</code> that matched the event. Similarly to the EventArgs problem above, I'd originally tried to create an  <code>EventHandler</code>, which failed for certain events.

The last piece is the <code>ControlAttributeName</code> method, which builds the desired attribute (in this case an event) name from a control and the ViewModel member that we want to bind to. The method assumes that the name of the ViewModel member (the handler) will start with the name of the control. If there's a match, it returns the rest of the member name. Otherwise, null. 
The name comparison ignores case, which wasn't necessary to hook up method handlers, but proved to be useful when wiring up properties.
{% highlight csharp %}
private string ControlAttributeName(Control control, MemberInfo viewModelMember)
{
    if ( viewModelMember.Name.ToLower().StartsWith(control.Name.ToLower()) )
    {
        return viewModelMember.Name.Substring(control.Name.Length);
    }
    return null;
}
{% endhighlight %}
<h2>What's next?</h2>
After wiring the event handlers, the ViewModelBase binds to the View's interesting properties. <a href="{{ site.url }}{% post_url 2010-11-10-growing-an-mvvm-framework-in-2003-part-ii-properties %}">Details to follow</a>.
