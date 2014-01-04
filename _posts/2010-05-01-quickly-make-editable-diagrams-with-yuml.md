---
layout: post
title: Quickly make editable diagrams with yUML
tags:
    - Development
    - PNG
    - yUML
---
I'm always on the lookout for convenient tools for creating diagrams that can be used for software development. <a href="http://www.balsamiq.com/">Balsamiq</a> is my tool of choice for UI mockups - it's great for whipping up stylized interfaces in very little time.

Balsamiq does a great job of simplifying mockup creation, since it takes a lot of choices away from the user - you don't have the ability to change fonts or line thicknesses or colours. It really lets you focus on the aspects of the interface that matter when you're just getting started - the types and relative positions of the screen elements.

Recently I discovered <a href="http://yuml.me/">yUML</a> - an online tool for creating class diagrams, activity diagrams, and use case diagrams. It's quite simple and produces attractive results. The best part is that you just specify the relationship between components - you don't have to position them yourself.

Using an example from the site, you can create a diagram that shows that:
<ul>
	<li>a single customer aggregates several orders,each of which</li>
	<li>uses 0 or 1 PaymentMethods, and</li>
	<li>is composed of some number of LineItems</li>
</ul>
by entering this code:

<pre>
[Customer]+1-&gt;*[Order]
[Order]++1-items &gt;*[LineItem]
[Order]-0..1&gt;[PaymentMethod]
</pre>

And out pops this diagram:

<div class="images">
  <img class="aligncenter size-full wp-image-414" title="yUML Order Example" src="{{ site.image_dir }}/yuml_order_example.png" alt="yUML Order Class Diagram" width="605" height="152" />
</div>

Over the years, I've become accustomed to using WYSIWYG tools to create written documents and images, but I often miss text-based tools. They:
<ul>
	<li>give consistent, repeatable results,</li>
	<li>allow easy diffing between versions, and</li>
	<li>don't encourage time-wasting as we fiddle to adjust every single pixel or line break</li>
</ul>
so I was really happy to find yUML - even though the syntax takes a little getting used to, it makes it easy to generate diagrams with a minimum of fuss.

One wrinkle I've had using tools like Balsamiq and yUML is going back to modify diagrams after I've saved them off as a PNG. The last time I posted a Balsamiq PNG, I resorted to <a href="{% post_url 2010-02-07-using-subversion-to-evangelize-powershell %}#getting_started">embedding the text that represented the diagram in the post comments</a>. Actually, don't bother clicking that link - I'm sure I had the source saved in the post as an HTML comment, but I don't see it there, not even in edit mode.

I've unwittingly demonstrated a point I was trying to make - many of these design tools don't allow you to save the "source" of the diagram, and it could be lost. This isn't a disaster for simple diagrams like the one above, but it could be very inconvenient for larger ones. Another problem is that typing out the code, pasting it into the conversion tool (in yUML's case a web page), and converting it and saving the result can become tedious as you make many adjustments.

To address some of these inconveniences, I created a tiny Python script that accepts a class diagram description, hits the yUML website to create an image from it, and saves the image to disk, embedding the diagram "source code" in the PNG's <a href="http://www.w3.org/TR/PNG/#11iTXt">iTXt chunk</a>:

{% highlight python %}
import urllib
import urllib2

import png

def add_yuml_to_png(yuml, in_stream, out_stream):
    signature = png.read_signature(in_stream)
    out_stream.write(signature)

    for chunk in png.all_chunks(in_stream):
        if chunk.chunk_type == 'IEND':
            break
        chunk.write(out_stream)

    itxt_chunk = png.iTXtChunk.create('yuml', yuml)
    itxt_chunk.write(out_stream)

    # write the IEND chunk
    chunk.write(out_stream)

def create(yuml, output_filename):
    baseUrl = 'http://yuml.me/diagram/scruffy/class/'
    url = baseUrl + urllib.quote(yuml)

    original_png = urllib2.urlopen(url)
    output_file = file(output_filename, 'wb')

    add_yuml_to_png(yuml, original_png, output_file)

    output_file.close()

if __name__ == '__main__':
    import sys
    sys.exit(create(*sys.argv[1:3]))
{% endhighlight %}

The <code>png</code> module is a very rudimentary PNG handling module that I wrote just for this script. There are ready-made Python PNG modules out there, but I thought they'd be too heavy to pull in for this, and that it'd be fun to write the PNG-handling code. It was.

Later on, when you want to adjust the diagram, we can the following command on the PNG:

<pre>
read_yuml_from_png.py yuml_order_example.png
[Customer]+1-&gt;*[Order], [Order]++1-items&gt;*[LineItem], [Order]-0..1&gt;[PaymentMethod]
</pre>

And here's read_yuml_from_png.py:

{% highlight python %}
import png

def read(pngFilename):
    yuml = '&lt;&lt;no yuml found&gt;&gt;'
    pngFile = file(pngFilename, 'rb')
    png.read_signature(pngFile)
    for chunk in png.all_chunks(pngFile):
        if chunk.chunk_type == 'iTXt':
            chunk = png.iTXtChunk(chunk)
            if chunk.keyword == 'yuml':
                yuml = chunk.text
                break
    pngFile.close()
    return yuml

if __name__ == '__main__':
    import sys
    sys.exit(read(sys.argv[1]))
{% endhighlight %}

and out pops the original class diagram description.

The <strong>png</strong> module is kind of long to paste here, but you can get all of the source for this post from <a href="http://code.google.com/p/blairconrad/source/browse/#svn/trunk/BlogExamples/2010-05-yuml-embed-text%3Fstate%3Dclosed">my Google code project</a> (<a href="https://blairconrad.googlecode.com/svn/trunk/BlogExamples/2010-05-yuml-embed-text">direct link to source</a>).
