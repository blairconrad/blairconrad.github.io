---
layout: post
title: How to completely disable Autofac components
comments: true
tags: .NET, Autofac, Development
---
This week I started working with the <a href="http://code.google.com/p/autofac/">Autofac</a> <a href="http://www.martinfowler.com/articles/injection.html">Inversion of Control container</a> at the Day Job. The first project I tried to introduce Autofac to needed a plugin system. I figured this was a perfect use of <a href="http://nblumhardt.com/2010/01/the-relationship-zoo/">Autofac's implicit relationship handlers</a>. Sure enough, a

<pre><code class="csharp">container.Resolve&lt;IEnumerable&lt;IPlugin&gt;&gt;()</code></pre>

did the trick - I got a nice list of plugin instances for the application to use.

This isn't enough, though. We need to disable certain components via configuration. One option would be to remove the components from the configuration file, but I wanted to make it easy to restore the plugins (and their original configuration) should the need arise. After poring over the Autofac documentation, it seemed like adding an "Enabled" flag in the components' metadata would be the best way to handle toggling them between on and off. 

Setting up the config file was straightforward,
<pre><code class="xml">&lt;autofac defaultAssembly="DisableComponents"&gt;
  &lt;components&gt;
    &lt;component type="DisableComponents.Plugin1" service="DisableComponents.IPlugin"&gt;
      &lt;metadata&gt;
        &lt;item name="Enabled" value="false" type="System.Boolean" /&gt;
      &lt;/metadata&gt;
    &lt;/component&gt;
    &lt;component type="DisableComponents.Plugin2" service="DisableComponents.IPlugin"&gt;
      &lt;metadata&gt;
        &lt;item name="Enabled" value="true" type="System.Boolean" /&gt;
      &lt;/metadata&gt;
    &lt;/component&gt;
  &lt;/components&gt;
&lt;/autofac&gt;</code></pre>

as was filtering the components list.

<pre><code class="csharp">var enabledComponents = container.Resolve&lt;IEnumerable&lt;Meta&lt;IPlugin&gt;&gt;&gt;()
    .Where(ComponentIsEnabled)
    .Select(c=&gt;c.Value);

...

private static bool ComponentIsEnabled&lt;T&gt;(Meta&lt;T&gt; component)
{
    const string enabled = "Enabled";
    return !component.Metadata.ContainsKey(enabled) || (bool)component.Metadata[enabled];
}</code></pre>

<h2>They're still created, though</h2>
This approach worked, but all all components are instantiated, including the disabled ones which are made just so we can throw them away. This seems a little wasteful. Worse, a particular installation may have a plugin disabled because it can't (or doesn't want to) support its creation. So I sought a way to prevent the instantiation of the unwanted plugins.

I tried to find a way to remove or disallow registration based on the metadata, or to intercept component creation, but came up short. The best I could come up with was a modification to the approach above:
<pre><code class="csharp">var enabledComponents = container.Resolve&lt;IEnumerable&lt;Meta&lt;Func&lt;IPlugin&gt;&gt;&gt;&gt;()
    .Where(ComponentIsEnabled)
    .Select(c=&gt;c.Value());</code></pre>

(I would have preferred to use a <a href="http://msdn.microsoft.com/en-us/library/dd642331.aspx">Lazy</a> over a <a href="http://msdn.microsoft.com/en-us/library/bb534960.aspx">Func</a>, but I'm working with .Net&nbsp;35.)

This works&mdash;the plugins are only created when they're enabled&mdash;but it feels inelegant.
I can't help but think that my Autofac knowledge is too shallow to have discovered the "right" way to do this. Hopefully deeper understanding will come in time&hellip;
