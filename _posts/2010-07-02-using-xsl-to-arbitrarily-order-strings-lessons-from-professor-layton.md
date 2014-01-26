---
layout: post
title: Using XSL to arbitrarily order strings - lessons from Professor Layton
comments: true
tags:
    - Development
    - Sorting
    - XSLT
---
At the Day Job,  I usually work on a middleware component that contains a component that monitors the state of the system. A "health check", if you will. The component can be monitored automatically so notifications can be triggered on error conditions, or it can be used by a human. In the latter case, the user sees a list of tests performed on the system, sorted first by test outcome and then by test name. To help the user identify problems, any errors encountered are pushed to the top of the results page. Here's a sample:

<table border="1" style="border:1px solid black;border-collapse:collapse;">
<tr style="background:#DDDDDD;"><th>Result</th><th>Test</th><th>Notes</th></tr>
<tr><td>Error</td><td>Nacelle Polarization</td><td>unpolarized</td></tr>
<tr><td>OK</td><td>Dilithium Crystals</td><td>&nbsp;</td></tr>
<tr><td>OK</td><td>Jefferies tube</td><td>&nbsp;</td></tr>
<tr><td>OK</td><td>Warp Coils</td><td>&nbsp;</td></tr>
</table>

The actual report is an HTML page built from XML using an XSL transform - the main health check page queries various subcomponents that provide XML document sections. The sections are gathered and the XSLT sorts the results according to severity.

The XSLT sorts the entries alphabetically by result string, using this XSL:
{% highlight xml %}
<xsl:apply-templates select="//Operation">
    <xsl:sort order="ascending" select="Result" />
    <xsl:sort order="ascending" select="Test" />
</xsl:apply-templates>
{% endhighlight %}
Up 'til now, that worked great, but recently we had a need to add a third status - "Warning". The new report looked like this:

<table border="1" style="border:1px solid black;border-collapse:collapse;">
<tr style="background:#DDDDDD;"><th>Result</th><th>Test</th><th>Notes</th></tr>
<tr><td>Error</td><td>Nacelle Polarization</td><td>unpolarized</td></tr>
<tr><td>OK</td><td>Dilithium Crystals</td><td>&nbsp;</td></tr>
<tr><td>OK</td><td>Warp Coils</td><td>&nbsp;</td></tr>
<tr><td>Warning</td><td>Jefferies tube</td><td>partly blocked</td></tr>
</table>

It would be better for Warning to be grouped between Error and OK. Unfortunately, it wasn't obvious how to do this. A few Google searches later, I'd found <a href="http://www.oxygenxml.com/archives/xsl-list/200603/msg00506.html">a post by Nick Fitzsimons that described his solution to the problem</a>. After trying his approach, I was struck by a feeling of deja vu: I'd seen this, and recently, but where?

<h2>Professor Layton to the Rescue</h2>

Then it hit me. It's a classic puzzle. I'm sure it's appeared in many places, but I recently saw it in the game <a href="http://professorlaytonds.com/">Professor Layton and the Diabolical Box</a>.

The Fake Coins puzzle asks
<blockquote>
There are 10 coins in each of the five bags below. One of these bags is filled with fake coins that are lighter than the real ones. A real coin weighs 10 units, but a false coin is one unit lighter. If you're  using a scale that can register up to 200 units, what is the fewest number of times you could use the scale to find the one bag filled with fake coins?
</blockquote>

<div class="images">
<a href="{{ site.image_dir }}/fake_coins.png"><img src="{{ site.image_dir }}/fake_coins.png" alt="fake coins puzzle" title="fake coins puzzle" width="256" height="192" class="aligncenter size-full wp-image-494" /></a>
</div>

I'm going to spoil the puzzle, so if you want to figure it out yourself, stop reading now.

The answer is "one". The interesting part is the approach: 
take 1 coin from bag 1, 2 coins from bag 2, and so on. Weigh them. There's a total of 15 coins, so if they were all genuine, the weight would be 150 units, but we know that each counterfeit coin is one unit less. So,
<ul>
<li>if bag 1 contains the fakes, the total weight will be 150 - 1 = 149</li>
<li>if bag 2 contains the fakes, the total weight will be 150 - 2 = 148</li>
<li>if bag 3 contains the fakes, the total weight will be 150 - 3 = 147</li>
<li>if bag 4 contains the fakes, the total weight will be 150 - 4 = 146</li>
<li>if bag 5 contains the fakes, the total weight will be 150 - 5 = 145</li>
</ul>

It's a nice trick - coins from each bag contribute either 10 or 9 units - the weight difference between a good and a bad coin is 1, so we magnify that constant difference by different amounts to produce a single value that identifies which group the fake(s) come from.

<h2>From coins to result severity</h2>

The puzzle's fun, but what's the connection with the string ordering? The <a href="http://www.w3.org/TR/xslt#sorting">XSLT sort function</a> operates on a single sort key generated from the input nodes, kind of like the single value (the weight) generated from a set of coins in the puzzle. 

It's still not clear how to generate a "weight" for the strings. Like in the coin puzzle, we want to sum up a series of values that are mostly the same, but that differ for a single result severity. We're helped by the fact that the <a href="http://www.w3.org/TR/xpath/#function-number">number function</a> converts Boolean <code>true</code> values to 1 and <code>false</code> to 0. If we compare each result severity in the source XML to "Error", "Warning", and "OK" in turn, exactly one of these will give a true (1) response, and the rest will be false (0). 

So, like the coin puzzle, where all weights are the same except for the counterfeits, we have a situation where all comparisons give the same value except for the true one. If we treat the sorting groups&mdash;Error, Warning, and OK&mdash;like the bags of coins, we can see how to rank the results. Multiplying the 0s and 1s by a factor that gives the preferred sort order produces a sum that acts as the perfect sort key:
{% highlight xml %}
<xsl:apply-templates select="//Operation">
    <xsl:sort data-type="number" order="ascending"
        select="(number(Result='Error') * 1)
              + (number(Result='Warning') * 2)
              + (number(Result='OK') * 3)" />
    <xsl:sort order="ascending" select="Result" />
</xsl:apply-templates>
{% endhighlight %}

<ul>
<li>a result severity of <b>Error</b> maps to 1 &times; 1 + 0 &times; 2 + 0 &times; 3 = <b>1</b></li>
<li>a result severity of <b>Warning</b> maps to 0 &times; 1 + 1 &times; 2 + 0 &times; 3 = <b>2</b></li>
<li>a result severity of <b>OK</b> maps to  0 &times; 1 + 0 &times; 2 + 1 &times; 3 = <b>3</b></li>
</ul>
The select code is a little long, and not obvious when starting from an empty slate, but it has some nice features:
<ul>
<li>extending the sort for new result severities is straightforward - just add a term with the appropriate multiplier</li>
<li>if we introduce a new severity without adding it to the sort, it sorts to the top - probably the best possible default action</li>
<li>most importantly, it works. We now get a good health check result:</li>
</ul>

<table border="1" style="border:1px solid black;border-collapse:collapse;">
<tr style="background:#DDDDDD;"><th>Result</th><th>Test</th><th>Notes</th></tr>
<tr><td>Error</td><td>Nacelle Polarization</td><td>unpolarized</td></tr>
<tr><td>Warning</td><td>Jefferies tube</td><td>partly blocked</td></tr>
<tr><td>OK</td><td>Dilithium Crystals</td><td>&nbsp;</td></tr>
<tr><td>OK</td><td>Warp Coils</td><td>&nbsp;</td></tr>
</table>
