MakeItEasy: Making SUTs with Minimal Fuss
#########################################

:tags: MakeItEasy, FakeItEasy, testing
:cover: {static}/images/makeiteasy-social-preview.png

Recently a `FakeItEasy <https://fakeiteasy.github.io/>`_ user came to our Gitter
channel asking about easier ways to create their
`systems under test <http://xunitpatterns.com/SUT.html>`_ and the Fakes that
those systems depend on. They referenced the old ``UnderTest`` and ``Fake``
attributes that FakeItEasy
`used to provide <https://thomaslevesque.com/2016/01/17/automatically-inject-fakes-in-test-fixture-with-fakeiteasy/>`_
for this purpose, but which had been removed when FakeItEasy 5.0.0 was released.

There are some existing libraries that provide this functionality, or something
like it, such as

- `AutoFixture.AutoFakeItEasy <https://github.com/AutoFixture/AutoFixture>`_,
- `Autofac.Extras.FakeItEasy <https://autofaccn.readthedocs.io/en/latest/integration/fakeiteasy.html>`_, and
- `FakeItEasy.Auto <https://jamiehumphries.github.io/FakeItEasy.Auto/>`_

but I thought there was room for improvement. The first two pull along
additional libraries with them, either for complete test data generation or for
generalized dependency injection. This isn't a problem (and may be a feature) if
you're already using those libraries, but could be overwhelming if you're not.
FakeItEasy.Auto has a nice light interface, but appears to be abandoned and only
supports .NET Framework 4.5.

So my FakeItEasy co-conspirator `Thomas Levesque <https://thomaslevesque.com/>`_
and I chatted about how to design a simple interface to create the system under
test. We (or if I'm being honest, mostly he) arrived at an API that

#. doesn't require the user to specify any arguments that they don't care about
#. doesn't require fields or properties on the test fixture, or use of any attributes
#. allows users to provide any values to the SUT's constructor
#. makes it easy to retrieve (and later configure) Faked collaborators

.. image:: {attach}makeiteasy-logo.png
    :alt: MakeItEasy Logo


Creating a System Under Test using MakeItEasy
=============================================

`MakeItEasy <https://github.com/blairconrad/MakeItEasy>`_ is an attempt to
fulfill the requirements laid out above. The ``Make`` class is its single entry
point and allows you to create your system under test:

.. code-figure:: The simplest way to create your system under test

    .. code:: c#

        import MakeItEasy;

        // ...

        var systemUnderTest = Make.A<VeryNeedySystem>().FromDefaults();


That's it. If ``VeryNeedySystem`` has a public constructor whose arguments can
be made from FakeItEasy Dummies, MakeItEasy will make it for you.
It doesn't matter if the constructor has 1 parameter or 14.


Making and Using Fake collaborators
===================================

The example above looks great, but more often you'll want to access the Fake
object(s) that the SUT will be using. Then you can configure them, or maybe
interrogate them after the system under test has been exercised. This is also
very easy:

.. code-figure:: Create a system under test and access a Fake collaborator

    .. code:: c#

        var systemUnderTest = Make.A<VeryNeedySystem>().From(
            out ICollaborator fakeCollaborator);

        // A.CallTo(() => fakeCollaborator.SomeMethod()).Returns(1);
        // exercise systemUnderTest
        // A.CallTo(() => fakeCollaborator.SomeMethod()).MustHaveHappened();

Currently MakeItEasy supports up to 8 ``out`` parameters, which will be
populated with Fakes and passed as constructor arguments to the system under
test.

You can even call ``Make`` from a setup method and initialize fields, if you
prefer not to use local variables for the collaborators.


Supplying Arbitrary Constructor arguments
=========================================

Maybe the system under test's constructor requires some non-Fake additional
parameters. MakeItEasy will usually populate these with Dummies, but if you have
a particular value you want to supply, you can do that:

.. code-figure:: Create a system under test using supplied arguments

    .. code:: c#

        var systemUnderTest = Make.A<VeryNeedySystem>().From(
            DateTime.Now);

You can supply up to 8 constructor arguments.


"Advanced" Usage
================

You can request Fake collaborators and supply arguments at the same time, of course.

.. code-figure:: Create a system under test specifying an argument and accessing a Fake collaborator

    .. code:: c#

        var systemUnderTest = Make.A<VeryNeedySystem>().From(
            DateTime.Now,
            out ICollaborator fakeCollaborator);

As before, you can supply up to 8 arguments and request up to 8 collaborators back.

MakeItEasy doesn't provide a way to customize the Fake before it's passed to the
constructor of the system under test. If you need this behaviour, you can always
create the Fake "by hand", configure it, and then pass it in. Or maybe you want
to share a Fake between systems under test. All this is supported, even in
combination.

.. code-figure:: Share Fakes between classes under test

    .. code:: c#

        var oneSystemUnderTest = Make.A<VeryNeedySystem>().From(
            out ICollaborator fakeCollaborator);
        
        // configure the fakeCollaborator somehow

        var anotherSystemUnderTest = Make.An<OtherKindOfSystem>().From(
            fakeCollaborator);


What Next?
==========

If you're interested in trying MakeItEasy, get `the latest release from NuGet
<https://www.nuget.org/packages/MakeItEasy/>`_. Tell me what you think. What
works for you? What doesn't? Chat here or
`raise an issue <https://github.com/blairconrad/MakeItEasy/issues>`_.
