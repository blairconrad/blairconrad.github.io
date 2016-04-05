---
layout: post
title: "Select May Not be Broken, But it's Bent" 
comments: true
tags: .NET
---

Earlier this week at the day job I ran into an interesting problem
working with a [DataTable][DataTable].  A view that's supposed to show
a subset of the table's rows showed nothing. I dropped into the
debugger and became even more confused.

Visually inspecting the DataTable showed that there was a row that
matched the filter the view was using, but running `Select` still
returned nothing. I didn't bring work's code home, but here's some
code that reproduces the problem:

<pre><code class="csharp">Console.Out.WriteLine("0th book's Library:\t{0}", books[0].Library);
Console.Out.WriteLine("# WPL books by Select:\t{0}", library.Books.Select("Library = 'WPL'").Length);
Console.Out.WriteLine("# WPL books by LINQ:\t{0}", library.Books.Count(book => book.Library == "WPL"));</code></pre>

And the output:

<pre>0th book's Library:     WPL
# WPL books by Select:  0
# WPL books by LINQ:    1</pre>

So, the table contains at least one book from [WPL][WPL], `Select`ing
for that library doesn't find the book, yet iterating over all the
rows and `Count`ing them does find it.

Just in case you think there's some whitespace trickery going on or
something, debug with me:

<figure>
  <img src="{{ site.image_dir }}/2015-10-05-select-may-not-be-broken/debugging.png">
</figure>

How is this happening? The row's Library property is actually
`DBNull`, but the dataset defines both `DefaultValue` and `NullValue`:

<figure>
  <img src="{{ site.image_dir }}/2015-10-05-select-may-not-be-broken/library_properties.png">
</figure>

So even though there was `DBNull` in the row, whenever I examined the
`Library` property, via code (such as the LINQ statements) or
visually in the debugger, it appeared to be "WPL".

`Select`, however, wasn't fooled. It knew the value was `DBNull` and
wouldn't match.

I'm of two minds about this. It's arguably _correct_ behaviour, as the
stored value is not "WPL", but I'm not sure that it's desirable to be
able to configure the table to present data in a way that's not
supported by the query.

[DataTable]: https://msdn.microsoft.com/en-us/library/system.data.datatable(v=vs.100).aspx
[WPL]: http://www.wpl.ca

