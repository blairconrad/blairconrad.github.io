---
layout: post
title: Prime Time Programming, Part 2
comments: true
tags: Development, Primes, Profiling, ProjectEuler, Python
---
<a href="{filename}2011-04-25-primes-part-1.md">Last time</a> I presented a truly horrible prime number generator I was using for <a href="http://projecteuler.net/">Project Euler</a> problems. Then I presented a revamped generator that used trial division. By adding various refinements to the generator, we saw the time required to generate primes less than 10<sup>7</sup> shrink from hours to 123 seconds. Today I'll describe a different approach that's even more effective.

<!--more-->

<h2>Attempt 2: Sieve of Eratosthenes</h2>
The Sieve of Eratosthenes is another method for finding prime numbers. 
The algorithm is basically this:
<ol>
<li>make a big array of numbers, from 2 to the highest prime you're hoping to find</li>
<li>look for the next number that's not crossed off</li>
<li>this number is your next prime</li>
<li>cross off every multiple of the number you just found</li>
<li>so long as the prime you just found is less than the square root of your limit, go to step 2</li>
<li>the uncrossed numbers are prime</li>
</ol>

Suppose we want primes less than or equal to 20. We start with this list:
<table>
<tr>
<td>2</td>
<td>3</td>
<td>4</td>
<td>5</td>
<td>6</td>
<td>7</td>
<td>8</td>
<td>9</td>
<td>10</td>
<td>11</td>
<td>12</td>
<td>13</td>
<td>14</td>
<td>15</td>
<td>16</td>
<td>17</td>
<td>18</td>
<td>19</td>
<td>20</td>
</tr>
</table>
The first uncrossed off number is 2. That's our first prime. Cross off all the multiples of 2 (believe it or not, the 4 is crossed off):
<table>
<tr>
<td><b>2</b></td>
<td>3</td>
<td><s><span style="color:#CCC;">4</span></s></td>
<td>5</td>
<td><s><span style="color:#CCC;">6</span></s></td>
<td>7</td>
<td><s><span style="color:#CCC;">8</span></s></td>
<td>9</td>
<td><s><span style="color:#CCC;">10</span></s></td>
<td>11</td>
<td><s><span style="color:#CCC;">12</span></s></td>
<td>13</td>
<td><s><span style="color:#CCC;">14</span></s></td>
<td>15</td>
<td><s><span style="color:#CCC;">16</span></s></td>
<td>17</td>
<td><s><span style="color:#CCC;">18</span></s></td>
<td>19</td>
<td><s><span style="color:#CCC;">20</span></s></td>
</tr>
</table>

The next uncrossed off number is 3. Cross off the multiples:
<table>
<tr>
<td><b>2</b></td>
<td><b>3</b></td>
<td><s><span style="color:#CCC;">4</span></s></td>
<td>5</td>
<td><s><span style="color:#CCC;">6</span></s></td>
<td>7</td>
<td><s><span style="color:#CCC;">8</span></s></td>
<td><s><span style="color:#CCC;">9</span></s></td>
<td><s><span style="color:#CCC;">10</span></s></td>
<td>11</td>
<td><s><span style="color:#CCC;">12</span></s></td>
<td>13</td>
<td><s><span style="color:#CCC;">14</span></s></td>
<td><s><span style="color:#CCC;">15</span></s></td>
<td><s><span style="color:#CCC;">16</span></s></td>
<td>17</td>
<td><s><span style="color:#CCC;">18</span></s></td>
<td>19</td>
<td><s><span style="color:#CCC;">20</span></s></td>
</tr>
</table>
Next, we have 5. Cross off its multiples (actually, they're already crossed off because they're all also multiples of either 2 or 3):

<table>
<tr>
<td><b>2</b></td>
<td><b>3</b></td>
<td><s><span style="color:#CCC;">4</span></s></td>
<td><b>5</b></td>
<td><s><span style="color:#CCC;">6</span></s></td>
<td>7</td>
<td><s><span style="color:#CCC;">8</span></s></td>
<td><s><span style="color:#CCC;">9</span></s></td>
<td><s><span style="color:#CCC;">10</span></s></td>
<td>11</td>
<td><s><span style="color:#CCC;">12</span></s></td>
<td>13</td>
<td><s><span style="color:#CCC;">14</span></s></td>
<td><s><span style="color:#CCC;">15</span></s></td>
<td><s><span style="color:#CCC;">16</span></s></td>
<td>17</td>
<td><s><span style="color:#CCC;">18</span></s></td>
<td>19</td>
<td><s><span style="color:#CCC;">20</span></s></td>
</tr>
</table>
5 is greater than &radic;20, so stop looping. All the uncrossed off numbers are prime:
<table>
<tr>
<td><b>2</b></td>
<td><b>3</b></td>
<td><s><span style="color:#CCC;">4</span></s></td>
<td><b>5</b></td>
<td><s><span style="color:#CCC;">6</span></s></td>
<td><b>7</b></td>
<td><s><span style="color:#CCC;">8</span></s></td>
<td><s><span style="color:#CCC;">9</span></s></td>
<td><s><span style="color:#CCC;">10</span></s></td>
<td><b>11</b></td>
<td><s><span style="color:#CCC;">12</span></s></td>
<td><b>13</b></td>
<td><s><span style="color:#CCC;">14</span></s></td>
<td><s><span style="color:#CCC;">15</span></s></td>
<td><s><span style="color:#CCC;">16</span></s></td>
<td><b>17</b></td>
<td><s><span style="color:#CCC;">18</span></s></td>
<td><b>19</b></td>
<td><s><span style="color:#CCC;">20</span></s></td>
</tr>
</table>

<h3>A "borrowed" implementation</h3>
The <a href="http://en.wikipedia.org/wiki/Sieve_of_Eratosthenes">wikipedia article</a> even provides a Python implementation, which I reproduce here in slightly altered form:

<pre><code class="python linenos=table">def eratosthenes_sieve(m):
    # Create a candidate list within which non-primes will be
    # marked as None; only candidates below sqrt(m) need be checked. 
    candidates = range(m+1)
    fin = int(m**0.5)
 
    # Loop over the candidates, marking out each multiple.
    for i in xrange(2, fin+1):
        if not candidates[i]:
            continue
 
        candidates[2*i::i] = [None] * (m//i - 1)
 
    # Filter out non-primes and return the list.
    return [i for i in candidates[2:] if i]</code></pre>
I ran this to find my standard list of primes less than 10<sup>7</sup>, and was surprised at the results. The time to completion varied wildly on successive runs. Sometimes over <b>50</b> seconds, and sometimes as low as <b>13</b>. I noticed that when the run times were high, the laptop's hard drive was thrashing, and just afterward my other applications were unresponsive. 

I reran the test and, with a little help from PerfMon, found out that the memory usage was off the chart. No, seriously. Right off the top. I had to rescale the graph to get everything to fit. the Private Bytes went way up over 200MB. On my 512 MB laptop with Firefox, emacs, and a few background processes, things slow to a crawl. With a smaller set of primes, or on more powerful iron, this implementation may work, but it's not going to meet my needs.

<h2>Attempt 3: The Sieve, but slowly cross out the composites</h2>
If allocating a big array of numbers just to cross most of them out right away doesn't work, how about we start by allocating nothing and just cross out numbers at the last moment?
The idea is pretty simple: start counting at 2, and keep a record of upcoming composite numbers that we've discovered by looking at multiples of primes so far. Essentially we maintain a rolling wave of the next multiples of 2, 3, 5, &hellip;:

<ol>
<li>let <code>composites = {}</code>, an empty associative array, where each key is a composite number and its value is the prime that it's a multiple of</li>
<li>let <code>n = 2</code></li>
<li>if n is a known composite, remove it and insert the next multiple in the list</li>
<li>otherwise, it's prime. Yield it and insert a new composite, <code>n<sup>2</sup></code></li>
<li>increment n</li>
<li>go to step 3</li>
</ol>

<h3>Let's see how it works</h3>
<table>
  <tr><th>n</th><th>composites</th></tr>
  <tr>
    <td>2</td><td><code>{}</code></td>
    <td><b>2</b> isn't in composites, so yield it. Then insert 2<sup>2</sup> = 4 and increment n.</td>
  </tr>
  <tr>
    <td>3</td><td><code>{4:2}</code></td>
    <td><b>3</b> isn't in composites, so yield it. Then insert 3<sup>2</sup> = 9 and increment n.</td>
  </tr>
  <tr>
    <td>4</td><td><code>{4:2, 9:3}</code></td>
    <td>4 is in composites, with value 2. Remove it, insert 4 + 2 = 6 and increment n.</td>
  </tr>
  <tr>
    <td>5</td><td><code>{6:2, 9:3}</code></td>
    <td><b>5</b> isn't in composites, so yield it. Then insert 5<sup>2</sup> = 25 and increment n.</td>
  </tr>
  <tr>
    <td>6</td><td><code>{6:2, 9:3, 25:5}</code></td>
    <td>6 is in composites, with value 2. Remove it, insert 6  + 2 = 8 and increment n.</td>
  </tr>
  <tr>
    <td>7</td><td><code>{8:2, 9:3, 25:5}</code></td>
    <td><b>7</b> isn't in composites, so yield it. Then insert 7<sup>2</sup> = 49 and increment n.</td>
  </tr>
  <tr>
    <td>8</td><td><code>{8:2, 9:3, 25:5, 49:7}</code></td>
    <td>8 is in composites, with value 2. Remove it, insert 8 + 2 = 10 and increment n.</td>
  </tr>
  <tr>
    <td>9</td><td><code>{9:3, 10:2, 25:5, 49:7}</code></td>
    <td>9 is in composites, with value 3. Remove it, insert 9 + 3 = 12 and increment n.</td>
  </tr>
  <tr>
    <td>10</td><td><code>{10:2, 12:3, 25:5, 49:7}</code></td>
    <td>10 is in composites, with value 2. Remove it, and... <b>wait</b>.</td>
  </tr>
</table>

12 is already in the list, because it's a multiple of 3.  We can't insert it. We'll have to amend the algorithm to account for collisions. If a multiple is already accounted for, keep moving until we find one that isn't in the list.

In this case, add another 2 to 12 to get 14 and insert it. Then increment n.
<table>
<tr><th>n</th><th>composites</th></tr>
<tr>
<td>11</td><td><code>{12:3, 14:2, 25:5, 49:7}</code></td>
<td><b>11</b> isn't in composites, so yield it, insert 11<sup>2</sup> = 121, increment n, and continue&hellip;</td>
</tr>
</table>

<h3>Show me the code</h3>
Here's an implementation of the <b>naive algorithm</b> presented above
<pre><code class="python linenos=table">def sieve():
    composites = {}
    n = 2
    while True:
        factor = composites.pop(n, None)
        if factor:
            q = n + factor
            while composites.has_key(q):
                q += factor
            composites[q] = factor
        else:
            # not there - prime
            composites[n*n] = n
            yield n
        n += 1</code></pre>
This implementation takes <b>26.8</b> seconds to generate all primes below 10<sup>7</sup>,  close to &#188; the time the best trial division algorithm took.

<h3>Why is this method so great?</h3>


* Using the associative array values to remember which "stream" of multiples each composite comes from means that the array is no bigger than the number of primes we've seen so far
* The primes can be yielded as soon they're found instead of waiting until the end
* Adding p<sup>2</sup> when we find a new prime cuts down on collisions but still ensures that we'll keep find all multiples of p, because 2p, 3p, &hellip;, (p-1)p will be weeded out as multiples of lower primes.
* There's very little wasted work - finding a new prime number takes O(1) operations - just checking that the number isn't in the associative array and adding the square to the array. Many composites will take more work, but an amount proportional to the number of distinct prime factors the number has. For example, 12 has prime factors 2, 2, and 3. We tried to add 12 to the array twice, once as a multiple of 2 and once as a multiple of 3. Fortunately, the number of distinct factors is severely limited. For numbers less than 10<sup>7</sup>, 9699690 has the most distinct prime factors: 2, 3, 5, 7, 11, 13, 17, 19. This sure beats the 446 divisions trial division took to find that 9999991 was prime.


The method already incorporates some of the advantages of the souped-up trial division methods from last time. We only worry about multiples of primes, so there's no need to cut out the composite factors. And when checking to see if n is prime, we never consider prime factors larger than &radic;n. Still, there are some optimizations to make.

<h3>That's Odd</h3>
In the sample runthrough above, the algorithm checks 4, 6, 8, 10, &hellip; for primality, even though no even number larger than 2 are prime. Here's an implementation that avoids that:
<pre><code class="python linenos=table">def odd_sieve():
   composites = {}
   yield 2
   n = 3
   while True:
       factor = composites.pop(n, None)
       if factor:
           q = n + 2 * factor
           while composites.has_key(q):
               q += 2 * factor
           composites[q] = factor
       else:
           # not there - prime
           composites[n*n] = n
           yield n
       n += 2</code></pre>

This method generates primes less than 10<sup>7</sup> in <b>13.4</b> seconds. This is about half the time it took when we didn't pre-filter the evens. In the trial division case, when we cut out the even numbers, we were saving almost no work - one division per even number, out of potentially dozens or hundreds of divisions being performed. This time, we cut out an associative array lookup and insertion, and most numbers are checked by using only a small number of these operations. Let's see what else we can do.

<h2>What about 3?</h2>

If skipping the numbers that are divisible by 2 paid off, will skipping those divisible by 3 as well? Probably.
<pre><code class="python linenos=table">def sixish_sieve():
    composites = {}
    yield 2
    yield 3
    step = 2
    n = 5
    while True:
        factor = composites.pop(n, None)
        if factor:
            q = n + 2 * factor
            while q % 6 == 3 or composites.has_key(q):
                q += 2 * factor
            composites[q] = factor
        else:
            # not there - prime
            composites[n*n] = n
            yield n
        n += step
        step = 6 - step</code></pre>
Now the time to generate primes less than 10<sup>7</sup> is <b>11.9</b> seconds. Again, I think we've hit diminishing returns. We didn't get the 1/3 reduction I'd hoped, probably due to the more complicated "next multiple" calculation.

<h3>YAGNI</h3>
Things are going pretty well. There's only one thing that bothers me about the latest generator - we're storing too many composites in the associative array. Every time we find a prime number, its square is inserted in the array. Even 9999991<sup>2</sup> is put in the array, even though we'll never check to see if any number greater than 10<sup>7</sup> is prime. So, modifying the algorithm to omit storing composites that are too large, we get:
<pre><code class="python linenos=table">def sixish_sieve_max():
    composites = {}
    yield 2
    yield 3
    step = 2
    n = 5
    while True:
        factor = composites.pop(n, None)
        if factor:
            q = n + 2 * factor
            while q % 6 == 3 or composites.has_key(q):
                q += 2 * factor
            composites[q] = factor
        else:
            # not there - prime
            if n*n <= highest:
                composites[n*n] = n
            yield n
        n += step
        step = 6 - step</code></pre>

This generator takes <b>10.8</b> seconds to generate primes below 10<sup>7</sup> - modest improvement, and one I'd keep anyhow, since the code is barely more complicated than the previous version. However, the real boost, if there is any, is in the memory usage. When <code>sixish_sieve</code>  generates primes below 10<sup>7</sup>, the private bytes climb up to 52MB, but <code>sixish_sieve_max</code> stays below 25MB. The advantage continues as the problem set grows - when the upper limit is 2*10<sup>7</sup>, <code>sixish_sieve</code> takes 100MB, but <code>sixish_sieve_max</code> remains at a cool 25MB - I guess that's the difference between storing 1270607 composites and 607.


<h2>Conclusion</h2>
This was a fun and interesting exercise. Being able to look bad at your old code and say "Boy, that was horrible. I'm glad I'm smarter now," makes me happy. And embarrassed. I enjoyed seeing how applying incremental changes and even rudimentary profiling yielded provably better results, right up until they showed that I probably needed to abandon my current path (trial division) and jump on a new one.

I'm sticking with <code>sixish_sieve_max</code> for now. It's fast enough to meet my current needs, and will likely remain so until "CPU inflation" forces the Project Euler team to increase the size of their problem sets. Of course, maybe by then <i>I'll</i> have a faster processor and I won't care.


