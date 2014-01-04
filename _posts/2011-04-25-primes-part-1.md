---
layout: post
title: Prime Time Programming, Part 1
tags:
    - Development
    - Primes
    - Profiling
    - ProjectEuler
    - Python
---
From time to time, I find myself caught up in the heady world of <a href="http://projecteuler.net/" title="Project Euler is a series of challenging mathematical/computer programming problems that will require more than just mathematical insights to solve. Although mathematics will help you arrive at elegant and efficient methods, the use of a computer and programming skills will be required to solve most problems.">Project Euler</a>. It's almost like playing <a href="http://professorlaytonds.com/">Professor Layton</a> or some other puzzle-solving game - mathematical or programming brain teasers, served in bite-sized pieces.

If you look at the Project Euler problems for any length of time, you'll notice common themes. One theme is <a href="http://en.wikipedia.org/wiki/Prime_number">prime numbers</a> - many problems can't be solved without generating varying quantities of primes. To that end, I'd written a prime generator to be shared between problem solutions. Over time, I added functionality and "optimized" the generator to improve the running time of my solutions. Everything was great, until I tried <a href="http://projecteuler.net/index.php?section=problems&id=315" title="Digital root clocks">Problem 315</a>, whose solution required a list of primes between 10<sup>7</sup> and 2&times;10<sup>7</sup>. My solution worked, but it ran really slowly - something like 12 minutes. Now, I'm not doing myself any favours by writing in Python and running on a 7-year-old laptop, but that's still too long.

<!--more-->

<h2>My Original Generator</h2>
This is the slow-performing generator that I replaced when working on Problem 315. The squeamish reader may want to avert his eyes.
{% highlight python %}
class PrimeGenerator:
    __primes_so_far = [5]
    __increment = 2

    def __init__(self):
        self.__next_index = -1


    def is_prime(self, n):
        if n == 2 or n == 3:
            return True
        elif n % 2 == 0 or n %3 == 0:
            return False
        elif n <= PrimeGenerator.__primes_so_far[-1]:
            # bisecting didn't really help
            return n in PrimeGenerator.__primes_so_far
        else:
            return self.__is_prime(n)

    def __is_prime(self, n):
        limit = math.sqrt(n)
        g = PrimeGenerator()
        g.next() # skip 2
        g.next() # skip 3
        p = g.next()
        while p <= limit:
            if  n % p == 0:
                return False
            p = g.next()
        return True
        
    def next(self):
        self.next = self.__next3
        return 2

    def __next3(self):
        self.next = self.__next5
        return 3

    def __next5(self):
        self.__next_index += 1
        if self.__next_index < len(PrimeGenerator.__primes_so_far):
            return PrimeGenerator.__primes_so_far[self.__next_index]
            
        candidate = PrimeGenerator.__primes_so_far[-1]

        while True:
            candidate += PrimeGenerator.__increment
            PrimeGenerator.__increment = 6 - PrimeGenerator.__increment
        
            if self.__is_prime(candidate):
                PrimeGenerator.__primes_so_far.append(candidate)
                return candidate

    def __iter__(self):
        return self
{% endhighlight %}

<h3>My eyes!</h3>
When I first went back to this code, I exclaimed, "What was I thinking?". I can think of two things:
<ol>
<li>The <code>is_prime</code> member was intended to help out for problems where I didn't have to create too many primes, but just had to check a few number for primality. This doesn't really belong here, and clutters the class. I'd be better off focusing on prime generation.</li>
<li>I was optimizing at least partly for the case where I'd want to get lists of primes a couple times&mdash;hence the indexing into an already-generated list of primes. If the generator were fast enough, this wouldn't be necessary.</li>
</ol>

Things I can't understand, even today. I'll have to blame them on then-ignorance, foolishness, and hasty modifications to the class:
<ul>
<li>Why the mucking about with <code>__next3</code> and <code>__next5</code>? What did I have against <a href="http://docs.python.org/reference/simple_stmts.html#yield">yield</a>?</li>
<li>Why is <code>is_prime</code> fussing with a whole new <code>PrimeGenerator</code> and skipping 2 and 3? Why not just go straight for the saved list of primes starting with 5?</li>
</ul>

In fact, just about the only defensible things (as we'll see below) in the whole class are:
<ul>
<li>ending the modulus checks once the candidate divisor is greater than the square root of the candidate number, and</li>
<li>the bit where the next<code>__increment</code> is formed by subtracting the current one from 6 - I was exploiting the fact that, past 3, for any prime <i>p</i>, p &equiv; 1 (mod 6) or p &equiv; 5 (mod 6).</li>
</ul>

<h3>How slow was it?</h3>
The generator took <b>551.763 seconds</b> to generate primes less than <b>10<sup>7</sup></b>, as measured by the following:
{% highlight python linenos=table %}
def run(f):
    global highest
    start = datetime.datetime.now()
    count = 1
    for p in f:
        count += 1
        if p > highest: break
    end = datetime.datetime.now()
    elapsed = end-start
    return highest, count, elapsed.seconds + (elapsed.microseconds/1000000.0)
{% endhighlight %}
Where <code>f</code> is an instance of <code>PrimeGenerator</code> passed into the <code>run</code> method, and <code>highest</code> is a global that's been set to 10<sup>7</sup>. 

<h2>Moving forward</h2>
Based on the extreme slowness and general horribleness of the code, I figured I'd be better off starting over. So, I chucked the generator and started afresh with the simplest generator I could write. I resolved to make incremental changes, ensuring that at each step, the code was:
<ol>
<li>correct (otherwise, why bother)</li>
<li>faster than the previous version</li>
<li>simple enough for me to understand</li>
</ol>
Let's see what happened.

<h2>Attempt 1: Trial Division</h2>
<a href="http://en.wikipedia.org/wiki/Trial_division">Trial division</a> is one of the simplest methods for generating primes&mdash;you start counting at 2, and if no smaller positive integers (other than 1) divide the current number, it's prime. The <b>naive implementation</b> is very simple.
{% highlight python linenos=table %}
def naive_trial():
    n = 2
    while True:
        may_be_prime = True
        for k in xrange(2, n):
            if n % k == 0:
                may_be_prime = False
                break
        if may_be_prime:
            yield n
        n += 1
{% endhighlight %}
This method takes <b>113.804 seconds</b> to generate primes below <b>100000</b>&mdash;I couldn't wait for the full 10<sup>7</sup> - it would probably be over 3 hours.

<h3>Trial until root</h3>
Fortunately, there are some pretty obvious optimizations one can make to the algorithm. The first comes from the observation that if there is a number k, 1 < k < n, that divides n, then there is a number j that divides n with 1 < j &le; &radic;n, so we can stop our trial once we've hit that point.

{% highlight python linenos=table %}
def trial_until_root():
    n = 2
    while True:
        may_be_prime = True
        for k in xrange(2, int(n**0.5)+1):
            if n % k == 0:
                may_be_prime = False
                break
        if may_be_prime:
            yield n
        n += 1
{% endhighlight %}
This method takes <b>468 seconds</b> to generate primes up to 10<sup>7</sup>. A definite improvement (and already faster my original generator), but there's still room for more.

<h3>Trial by primes</h3>
Here's another observation about divisors of n: if there's a number k that divides n, then there's a prime number p &le; k that divides n, since either k is prime or has prime factors. So if we keep a list of the primes found so far, we only need to check prime divisors that are less than &radic;n.

{% highlight python linenos=table %}
def trial_by_primes():
    primes_so_far = []
    n = 2
    while True:
        may_be_prime = True
        for p in primes_so_far:
            if n % p == 0:
                may_be_prime = False
                break
            if p * p > n: # it's prime
                break
        if may_be_prime:
            primes_so_far.append(n)
            yield n
        n += 1
{% endhighlight %}

Now we're down to <b>136 seconds</b> to generate primes below 10<sup>7</sup>. That was a worthwhile change, but we have to balance it against the fact that the generator now requires additional storage - the list of primes encountered so far. In this case, we're storing over 660,000 prime numbers in a list. Even an older laptop can handle this burden, but it's something to keep in mind.

<h3>That's odd</h3>
And by "that", I mean "all the prime numbers except for 2". There's no point checking the even numbers to see if they're prime. Let's see what happens when we skip them. The only tricky part (and it's not that tricky) is to make sure we still return 2 as our first prime.

{% highlight python linenos=table %}
def odd_trial_by_primes():
    primes_so_far = []
    yield 2
    n = 3
    while True:
        may_be_prime = True
        for p in primes_so_far:
            if n % p == 0:
                may_be_prime = False
                break
            if p * p > n: # it's prime
                break
        if may_be_prime:
            primes_so_far.append(n)
            yield n
        n += 2
{% endhighlight %}
This method takes <b>127 seconds</b> to generate primes less than 10<sup>7</sup>. Not a huge improvement, but better than nothing, and it doesn't really complicate the code that much.  I'll keep it. The reason we don't get a huge improvement here is that checking the even numbers for primeness doesn't take that much effort - they were eliminated as soon as we modded them by the first prime in <code>primes_so_far</code>. Still, it's a little quicker to jump right over them than to perform the division.

<h3>What about 3?</h3>
If skipping the numbers that are divisible by 2 paid off, will skipping those divisible by 3? As I noted above, every prime <i>p</i> greater than 3 satisfies <code>p &equiv; 1 (mod 6) or p &equiv; 5 (mod 6)</code>. Let's use that. We'll take advantage of these facts:
<ul>
<li>if p &equiv; 1 (mod 6) , then p+4 &equiv; 5 (mod 6)</li>
<li>if p &equiv; 5 (mod 6) , then p+2 &equiv; 1 (mod 6)</li>
</ul>
So we want to alternate our <code>step</code> between 2 and 4. Fortunately 6 - 4 = 2 and 6 - 2 = 4, so we can use 6 - step as our next step.
{% highlight python linenos=table %}
def sixish_trial_by_primes():
    primes_so_far = []
    yield 2
    yield 3
    step = 2
    n = 5
    while True:
        may_be_prime = True
        for p in primes_so_far:
            if n % p == 0:
                may_be_prime = False
                break
            if p * p > n: # it's prime
                break
        if may_be_prime:
            primes_so_far.append(n)
            yield n
        n += step
        step = 6 - step
{% endhighlight %}
Now the time drops to <b>123</b> seconds to generate primes less than 10<sup>7</sup>. Clearly we've hit diminishing returns - we're saving two modulus operations on numbers that are divisible by 3 (but not 2), at the cost of a more complicated "step" calculation. We could continue on in this vein, but the gains are not likely to be large, and the complexity increases rapidly. Consider the next step: we'd make sure we don't test numbers divisible by 2, 3, or 5. That means (after 5) we only consider numbers whose remainders when divided by 30 are one of 1, 7, 11, 13, 17, 19, 23, or 29. The steps between numbers are 6, 4, 2, 4, 2, 4, 6, and 2. Who has the energy?
<h2>The problem with Trial Division</h2>
Trial division has a few things going for it:
<ul>
<li>it's simple to understand</li>
<li>there are some obvious optimizations that can make its performance tolerable</li>
</ul>
Ultimately, though, its downfall is that it takes a lot of work to verify that a large number is prime. Consider the largest prime number below 10<sup>7</sup>: 9999991. In order to verify that this is prime, we have to consider all prime factors less than &radic;9999991. There are 446 of these. That's 446 divisions, just to verify that one number is prime. 

We're unlikely to radically improve performance by continuing to tinker with trial division. It's time to throw the whole thing away again and try a new approach. Next time we'll do just that.
