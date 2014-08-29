---
layout: post
title: "Making a Duck-Dog using FakeItEasy's CallsBaseMethod(s)" 
comments: true
tags:
    - FakeItEasy
    - .NET
---

A while back, Roman Turovskyy wrote
[FakeItEasy: Be Careful When Wrapping an Existing Object][wrapping],
an interesting post highlighting some of the difficulties of faking
classes (as opposed to interfaces, which by virtue of having no
behaviour of their own, are quite a bit more predictable). It's
well-written and I enjoyed it, but he overlooked a small point. I
figured others may easily make the same omission, so I'd like to
explain why the example from that post works as it does, and to
provide an alternative solution.

----

Mr. Turovskyy supposes we want to fake out the following `Dog` class:

{% highlight csharp %}
public class Dog
{
    public virtual string Bark()
    {
        return "Bark!";
    }
    public virtual string BarkBark()
    {
        return Bark() + Bark();
    }
}
{% endhighlight %}

He notes that the default behaviour of a fake Dog, as made by `dog =
A.Fake<Dog>()`, is for both `Bark` and `BarkBark` to return the empty
string, which is not always desirable.

His next step is to create a fake by **wrapping a Dog object**:

{% highlight csharp %}
Dog realDog = newDog();
Dog dog = A.Fake<Dog>(x => x.Wrapping(realDog));
{% endhighlight %}

Now `Bark` and `BarkBark` return the original (expected) strings.

Then Mr. Turovskyy addresses customizing the fake object to change
the way it barks.

Here, things break down a little bit. His desired goal, of using
`A.CallTo` to override `Bark` to return "Quack!" works, but when
`BarkBark` is called, it **still returns "Bark!Bark!"**.


He comments

> For those who know how virtual methods work, this looks very
> counter-intuitive.

And that's completely true. The problem is that **when a fake wraps an
object, we're using a composition model, not inheritance**. Thus the
fake Dog knows to call the real dog's `BarkBark` method, but _the real
dog doesn't know about the fake Dog at all_, so it just calls its own
`Bark` method, which returns "Bark!".

Using the `Wrapping` option and then overriding `Bark` on the fake is
equivalent to writing this manual wrapper:

{% highlight csharp %}
public class WrappingDog: Dog
{
    private readonly Dog realDog;

    public WrappingDog(Dog realDog)
    {
        this.realDog = realDog;
    }

    public override string Bark()
    {
        return "Quack!";
    }

    public override string BarkBark()
    {
        return this.realDog.BarkBark();
    }
}
{% endhighlight %}


Mr. Turovskyy suggests getting the desired behaviour by writing a
manual `FakeDog` that overrides `Bark`, which will work, but is
tedious and discards the benefits that FakeItEasy can provide.

## Another Way to Access Original Behaviour

FakeItEasy can be used to get the desired behaviour. It provides a
`CallsBaseMethod` method when configuring a fake. It does just what
you'd hope it would. Witness:

{% highlight csharp %}
Dog dog = A.Fake<Dog>();
A.CallTo(() => dog.BarkBark()).CallsBaseMethod();
{% endhighlight %}

This tells the fake Dog to call the real `Dog.BarkBark` when its
`BarkBark` method is invoked. When this is combined with an override
for `Bark`, we can write this passing test:

{% highlight csharp %}
[Test]
public void BarkBark_CallsBaseMethod_UsesOverriddenBark()
{
    Dog dog = A.Fake<Dog>();

    A.CallTo(() => dog.BarkBark()).CallsBaseMethod();
    A.CallTo(() => dog.Bark()).Returns("Quack!");

    string result = dog.BarkBark();

    Assert.That(result, Is.EqualTo("Quack!Quack!"));
}
{% endhighlight %}

## Call Base Methods More Conveniently

As of [FakeItEasy 1.24.0][onetwentyfour], there's an additional way to
do this, and it may appeal more to users who want many methods on
their fake to call the original class's version. There's a new
[fake creation option][options] called [`CallsBaseMethods`][callsbasemethods]. It was
[proposed][issue] by [Aleksander Heintz][alexandr], who also provided
nearly the complete implementation. When used, it will cause _every_
method on a fake to delegate to the faked type's implementation, if there
is one. So the previous test could be written as

{% highlight csharp %}
[Test]
public void BarkBark_CallsBaseMethod_UsesOverriddenBark()
{
    Dog dog = A.Fake<Dog>(options => options.CallsBaseMethods());

    A.CallTo(() => dog.Bark()).Returns("Quack!");

    string result = dog.BarkBark();

    Assert.That(result, Is.EqualTo("Quack!Quack!"));
}
{% endhighlight %}

The change in the first line means that when `dog` is created, every
method will delegate to the version on `Dog`.

Then `Bark` is overridden, and the base `BarkBark` is able to use the
new version.

Now we can realize our dream of having a
[Seussian DuckDog][duckdog]:
<figure>
  <img src="{{ site.image_dir }}/Duck-Dog.jpg">
</figure>

[duckdog]: http://seuss.wikia.com/wiki/Duck-Dog
[wrapping]: http://elekslabs.com/2014/03/fakeiteasy-be-careful-when-wrapping.html
[onetwentyfour]: https://github.com/FakeItEasy/FakeItEasy/releases/tag/1.24.0
[options]: https://github.com/FakeItEasy/FakeItEasy/wiki/Creating-Fakes#options
[alexandr]: http://alxandr.me/
[issue]: https://github.com/FakeItEasy/FakeItEasy/issues/192
[callsbasemethods]: https://github.com/FakeItEasy/FakeItEasy/wiki/Calling-base-methods#configuring-all-methods-at-once
