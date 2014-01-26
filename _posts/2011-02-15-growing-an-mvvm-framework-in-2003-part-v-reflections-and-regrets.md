---
layout: post
title: Growing an MVVM Framework in 2003, part V&mdash;Reflections and Regrets
comments: true
tags:
    - .NET
    - Development
    - Frameworks
    - MVVM
---
<div style="padding-left:.5em;padding-right:.5em;margin-left:2em;margin-right:2em;border:1px solid #EEE;background-color:#F8F8F8;">
<p>This post is from a series on my experiences starting to grow an MVVM Framework in .NET 1.1.</p>

* <a href="{{ site.url }}{% post_url 2010-10-29-growing-an-mvvm-framework-in-2003-part-i-event-handlers %}">Part I&mdash;Event Handlers</a>
* <a href="{{ site.url }}{% post_url 2010-11-10-growing-an-mvvm-framework-in-2003-part-ii-properties %}">Part II &mdash; Properties</a>
* <a href="{{ site.url }}{% post_url 2010-11-21-growing-an-mvvm-framework-in-2003-part-iii-properties-redux %}">Part III  &mdash; Properties Redux</a>
* <a href="{{ site.url }}{% post_url 2010-11-30-growing-an-mvvm-framework-in-2003-part-iv-unit-tests %}">Part IV&mdash;Unit Tests</a>
* Part V&mdash;Reflections and Regrets

<p>Full source code can be found in my <a href="http://code.google.com/p/blairconrad/source/browse/#svn/trunk/BlogExamples/2010-11-mvvm-.net1.1/BookFinder">Google Code repository</a>.</p>
</div>

I haven't added any articles to this series in a while. The main reason is that I've not done any more work on the framework. I was able to complete my application using the tools using the Framework So Far, and I've long since moved on to other projects.  I wanted, though, to take a quick look back and evaluate the project.

<h2>I did it!</h2>
Way back in part&nbsp;1, I said that I wanted to create an application that 

* had testable logic, even in the GUI layer,
* had no “codebehind” in the view, and
* shunted the tedious wiring up of events and handlers into helpers (or a “framework”)

I'm very pleased with how all this turned out. Taking things in reverse order:

* The little framework does an excellent job of handling the tedious event-wiring. Handling an View event requires nothing more than declaring a method with a convention-following name and the correct signature, such as `public void FindClick(object sender, EventArgs e)`
Properties are wired up in a similar way, by declaring a public field with a convention-following name and an appropriate type (StringProperty, BoolProperty, or ListProperty).
* Aside from setting some properties on View elements (for example, the Find button is initial disabled), there was no need to crack open the View's .cs file&mdash;I never saw the inside of it.
* The easily-invoked event handlers and the property bindings made writing unit test as easy as writing tests for a non-GUI component: set some initial properties, poke the ViewModel by invoking an event handler, and check the properties. Done! Injecting mock model components was the hardest thing, and that's no different than in any other test.

<h2>If only I had</h2>
There was one nagging problem that I left unresolved. My Model contains only synchronous operations, so the View doesn't update while we're accessing the data store. As it turns out, the operations are very quick, so the user is unlikely to notice. 

I could have implemented asynchronous operations on the view, or used delgates or background threads to explicitly invoke the model in the background. I really would've liked to implement something that would be applicable to a larger problem set. Something like <a href="http://devlicio.us/blogs/rob_eisenberg/archive/2010/08/21/caliburn-micro-soup-to-nuts-part-5-iresult-and-coroutines.aspx">Caliburn.Micro's IResult and Coroutines</a>: 
Returning an <code>IResult</code> or a collection of them to be executed on background threads by the framework, while the GUI updates and the ViewModel is none the wiser.

Ah well, time was running out, and there didn't seem to be that much benefit. Maybe next time...

<h2>I would have liked to</h2>
There are a few other "features" that I would've liked to add to the framework, but there wasn't time, nor did there seem to be an immediate need:

* **a View binder** &mdash; After writing a class to bind the ViewModel to the fake storage properties, I realized that that was a nicer approach than having the binding code in the  ViewModelBase. I'd like create a "production binder" to hook up the ViewModel and View.
* **composable ViewModels** &mdash; BookFinder is very simple, with only a TextBox and a few ListBoxes and Buttons on its View, so a single View and ViewModel was sufficient. It would be useful to be able to build up a more complicated GUI by walking a tree of ViewModels and composing a GUI out of corresponding View components.
* **deregistering event handlers** &mdash; The framework registers event handlers between the ViewModel and View, with no provision for unregistering them when components are no longer needed. In BookFinder, the single View/ViewModel pair hang around until the application is closed, but in a more complicated application there might be an opportunity to leak resources.


<h2>Summing up</h2>
I'm happy with how the framework and tool turned out. I could probably have written the application more quickly if I hadn't bothered trying to extract the framework, but it wouldn't have been as testable (and therefore likely not as well tested). I think the extra effort was worthwhile both because it created a better application and because I learned more about WinForms programming and how I can leverage conventions to reduce programmer workload&mdash;if the framework were used for a second application, development would just fly. And the exercise was fun. Not only writing the framework, but using it &mdash; it's extremely liberating having event handlers just work by creating a properly-named method, and having the handler be immediately testable is a joy. If I had any expectations that I'd be writing similar tools on .NET&nbsp;1.1 again, I'd definitely continue extending the framework.


