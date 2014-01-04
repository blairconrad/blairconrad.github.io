---
layout: post
title: When Fields are Initialized, or "Lies Reflector Told Me"
tags:
    - .NET
    - C#
    - Development
    - Reflector
---
<p>The other day a coworker came to me with a Tricky Language Question. He and another chap had just finished working through a bug that had arisen due to a misunderstanding of C# constructor and field initialization order. The question?</p>

>In a derived class, when does field initialization occur, relative the derived and base constructor code?

<p>Specifically, what does this output?</p>

{% highlight csharp %}
class Print
{
    public Print(string message)
    {
        Console.Out.WriteLine(message);
    }
}

class Base
{
    public Print baseField = new Print(&quot;Base Field&quot;);
    public Base()
    {
        new Print(&quot;Base Constructor&quot;);
    }
}

class Derived: Base
{
    public Print derivedField = new Print(&quot;Derived Field&quot;);
    public Derived()
    {
        new Print(&quot;Derived Constructor&quot;);
    }
}
class Program
{
    static void Main()
    {
        new Derived();
    }
}
{% endhighlight %}

<p>I don't often give much thought to the "field vs. base class constructor" thing, but I knew that the Base constructor would be called before the Derived constructor, and I'd seen disassembled code in <a href="http://www.red-gate.com/products/reflector/">Reflector</a> that showed field initialization as if it were the first code executed in a  constructor. My guess was:</p>
<ul>
<li>Base Field</li>
<li>Base Constructor</li>
<li>Derived Field</li>
<li>Derived Constructor</li>
</ul>

<p>"Not so," said my coworker. The actual order is</p>
<ul>
<li>Derived Field</li>
<li>Base Field</li>
<li>Base Constructor</li>
<li>Derived Constructor</li>
</ul>

<p>The reason for this is given in <a href="http://www.ecma-international.org/publications/standards/Ecma-334.htm">C# Language Specification</a> section 17.10.3, <i>Constructor execution</i>:</p>

>Variable initializers are transformed into assignment statements, and these assignment statements are executed before the invocation of the base class instance constructor. This ordering ensures that all instance fields are initialized by their variable initializers before any statements that have access to that instance are executed.

<p>"What's the problem here?" you may be wondering - the Base code doesn't know anything about the Derived fields, so why go out of our way to make sure the field initializers are called before the Derived constructor?</p>
<h4>Vitual methods</h4>
<p>Virtual methods are the problem. If a virtual method is defined in Base and overridden in Derived, the overridden method may reference the new fields added to Derived. If the virtual method is called from the Base constructor, then we need those fields to be initialized <i>before</i> the constructor is called. Initializing fields even before calling base class constructors ensures that this is so.</p>

<p>Or does it? What if the field I'm accessing in a overridden method in the derived class doesn't have a field initializer, that method is called from the base constructor, and the field value is set in the derived constructor? In this case, the field won't be initialized before the method is called - it will still have the default value for its type.</p>

<p>So how to do we safely call virtual methods in constructors? We don't. You can't guarantee what code is going to go into a derived class's virtual method, so you never know what's going to happen.</p>

<h4>Back to Reflector</h4>
<p>Remember a few paragraphs ago when I said that Reflector told me that field initialization acted like it was an assignment statement at the beginning of a constructor? Well, I did, and I wanted to see whether I was misremembering, so I compiled my sample code and threw the assembly into Reflector. Here's what I saw:</p>

<a href="http://blairconrad.files.wordpress.com/2010/05/derived_class_constructor.png"><img src="http://blairconrad.files.wordpress.com/2010/05/derived_class_constructor.png" alt="Derived Class Constructor" title="Derived Class Constructor" width="248" height="75" class="size-full wp-image-440" /></a>

<p>I felt somewhat vindicated - this matched my memory. For a lark, I took this code (and the matching code Reflector showed me for the Base class), compiled it, ran it, and got:</p>
<ul>
<li>Base Field</li>
<li>Base Constructor</li>
<li>Derived Field</li>
<li>Derived Constructor</li>
</ul>

<p>The more I thought about this, though, the worse I felt. How could Reflector let me down like this? Isn't it just looking at the IL and translating into C#? I poked around a little more, and instead of just double-clicking on the Derived constructor, I right-clicked on the Derived class node in the navigation tree and picked <b>Disassemble</b>. Lo and behold:</p>

<a href="http://blairconrad.files.wordpress.com/2010/05/derived_class_whole.png"><img src="http://blairconrad.files.wordpress.com/2010/05/derived_class_whole.png" alt="Disassembled Derived Class" title="Disassembled Derived Class" width="294" height="154" class="size-full wp-image-441" /></a>

So, Reflector does know what's going on&mdash;you just have to ask nice. To recap,

* if you know which Reflector action to choose,
* you remember about field initializers running before even base class constructors, and
* you keep careful track of virtual methods called from constructors

Reflector can tell you what's going on in your code. Forget any of those things, and you're lost.
