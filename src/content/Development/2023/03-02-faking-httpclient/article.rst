Faking HttpClient Using FakeItEasy
##################################

:tags: FakeItEasy

Recently in the `FakeItEasy gitter channel <https://app.gitter.im/#/room/#FakeItEasy_FakeItEasy:gitter.im>`_,
someone asked how to fake
`System.Net.Http.HttpClient <https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclient?view=net-7.0>`_.

This is a question that comes up from time to time, and each time I have to fumble for an answer and search
old StackOverflow answers (usually for an older version of HttpClient) and the like. Today I'm writing
an answer down so it's easier to find.

.. block-info:: A note on versions

    Everything below has been tested using FakeItEasy 7.3.1 and .NET 7.0. As always, things may be different
    in the future. (Or past!)

Let's assume that you want to create a fake ``HttpClient`` so you can dictate the behaviour of the
`GetAsync(String) <https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclient.getasync?view=net-7.0#system-net-http-httpclient-getasync(system-string)>`_
method. Other methods work similarly. This seems like it would be a straightforward task,
but it's complicated by the design of ``HttpClient``, which is not faking-friendly.

A working Fake
==============

First off, let's look at the declaration of ``GetAsync``:

.. code:: c#

    public Task<HttpResponseMessage> GetAsync([StringSyntax(StringSyntaxAttribute.Uri)] string? requestUri)

This method is neither virtual nor abstract, and so
`can't be overridden by FakeItEasy <https://fakeiteasy.github.io/docs/stable/what-can-be-faked/#what-members-can-be-overridden>`_.

This could be the end of the story, but we can look at the
`definition of GetAsync <https://github.com/dotnet/runtime/blob/ab5e28c1cab305450897749daa7393bef30d7505/src/libraries/System.Net.Http/src/System/Net/Http/HttpClient.cs#L363-L364>`_
and see that we eventually end up calling
`HttpMessageHandler.SendAsync(HttpRequestMessage, CancellationToken) <https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpmessagehandler.sendasync?view=net-7.0#system-net-http-httpmessagehandler-sendasync(system-net-http-httprequestmessage-system-threading-cancellationtoken)>`_
on an ``HttpMessageHandler`` that can be supplied via the ``HttpClient`` constructor.

The downside is that ``HttpMessageHandler.SendAsync`` is protected, which makes it less convenient to
override than a public method. We need to specify the call by name, and to give FakeItEasy a hint about the return type,
as described in `Specifying a call to any method or property <https://fakeiteasy.github.io/docs/stable/specifying-a-call-to-configure/#specifying-a-call-to-any-method-or-property>`_.

Now we can write the following passing test:

.. code:: c#

    public async Task Test()
    {
        var response = new HttpResponseMessage { Content = new StringContent("FakeItEasy is fun") };

        var handler = A.Fake<HttpMessageHandler>();
        A.CallTo(handler)
            .WithReturnType<Task<HttpResponseMessage>>()
            .Where(call => call.Method.Name == "SendAsync")
            .Returns(response);

        var client = new HttpClient(handler);

        var result = await client.GetAsync("https://fakeiteasy.github.io/docs/");
        var content = await result.Content.ReadAsStringAsync();
        content.Should().Be("FakeItEasy is fun");
    }

.. block-warning:: This is a simplified example

    In the interest of brevity, I'm creating a Fake, exercising it directly, and checking its behaviour.
    A more realistic example would create the Fake as a collaborator of some production class (the "system
    under test") and the Fake would not be called directly from the test code.

Easier and safer call configuration
===================================

The above code works, but specifying the method name and return type is a little awkward.
A ``FakeableHttpMessageHandler`` class can be used to clean things up and to also supply a
little compile-time safety by ensuring we're configuring the expected method.
(Note: this class is a near-verbatim copy of the one written by FakeItEasy
co-owner `Thomas Levesque <https://thomaslevesque.com/>`_ while we were answering the user's question.)

.. code:: c#
    :hl-lines: 16 17 18

    public abstract class FakeableHttpMessageHandler : HttpMessageHandler
    {
        // sealed so when FakeItEasy creates a Fake, it won't intercept calls
        protected sealed override Task<HttpResponseMessage> SendAsync(
                HttpRequestMessage request, CancellationToken cancellationToken
            ) => FakeSendAsync(request, cancellationToken);

        public abstract Task<HttpResponseMessage> FakeSendAsync(
            HttpRequestMessage request, CancellationToken cancellationToken);
    }

    public async Task Test()
    {
        var response = new HttpResponseMessage { Content = new StringContent("FakeItEasy is fun") };

        var handler = A.Fake<FakeableHttpMessageHandler>();
        A.CallTo(() => handler.FakeSendAsync(A<HttpRequestMessage>.Ignored, A<CancellationToken>.Ignored))
            .Returns(response);

        var client = new HttpClient(handler);

        var result = await client.GetAsync("https://fakeiteasy.github.io/docs/");
        var content = await result.Content.ReadAsStringAsync();
        content.Should().Be("FakeItEasy is fun");
    }

Alternative: wrap HttpClient
============================

The above approach will work, but is a little cumbersome, and relies on the internal
implementation of ``HttpClient`` remaining the same. Assuming the interfaces of the
production code can be changed, one way to reduce uncertainty and
future-proof the code is to introduce a layer of abstraction on top of ``HttpClient``.
Since the wrapper could only be tested by faking `HttpClient`, which is what got us
into this mess, or by actually making web requests, we keep the implementation as
simple as possible and either lightly test the wrapper or leave it untested.

.. code:: c#

    public interface IWebStringGetter
    {
        Task<string> GetAsync(String requestUri);
    }

    public class WebStringGetter : IWebStringGetter
    {
        private readonly HttpClient client;

        public WebStringGetter(HttpClient client) => this.client = client;

        public async Task<string> GetAsync(string requestUri) =>
            await client.GetAsync(requestUri).Result.Content.ReadAsStringAsync();
    }

    public async Task Test()
    {
        var getter = A.Fake<IWebStringGetter>();
        A.CallTo(() => getter.GetAsync("https://fakeiteasy.github.io/docs/"))
            .Returns("FakeItEasy is fun");

        var text = await getter.GetAsync("https://fakeiteasy.github.io/docs/");
        text.Should().Be("FakeItEasy is fun");
    }

This results in a much simpler test, and so long as the ``HttpClient`` doesn't change its interface,
it will continue to work. Moreover, this technique is applicable to all kinds of difficult-to-fake
collaborators.