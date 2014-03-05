---
layout: post
title: Math item markup
categories: [information]
---
The markup to use when editing math items is based on [Markdown](http://daringfireball.net/projects/markdown/). All the markup of Markdown is supported, except for inline HTML, links and images.<span/>

### Basics
A paragraph is simply one or more consecutive lines of text, separated by one or more blank lines.

Words can be in *italics* or **boldface** by using `*single asterisks*` or `**double asterisks**`, respectively.

Section headers can be written as

    # This is a level 1 header

    ## This is a level 2 header

    ###### This is a level 6 header
    
where one to six hash characters determine the header level.

Lists can be written as

    * Item one
    * Item two
    * Item three

or using numbering,

    1. Item one
    2. Item two
    3. Item three
    
### Mathematics

Mathematics can be included like it would be in a (La)TeX document using $-signs. This includes inline math

    this formula $e^{-x^2}$ is an example of inline math
    
which will render as

> this formula {% inline_math e^{-x^2} %} is an example of inline math

and display math

    ... from which we obtain
    $$
    \sum_{k=1}^n \frac{1}{k^2}
    $$
    for positive $n$.

which will render as
    
> ... from which we obtain
> 
> {% display_math \sum_{k=1}^n %}
> 
> for positive {% inline_math n %}.

### References

References to other math items can be inserted using `[@T3456]` or `[Text to display@T3456]`. Both examples will link to item "T3456", but the displayed link text will be *abcd* and *Text to display*, respectively.

Abstract definitions can be referenced as `[#bounded set]` or `[bounded#bounded set]`. Both examples will link to a definition <a href="http://blog.teoremer.com/2013/12/03/on-categories.html">category</a> through the keyword *bounded set*, but the displayed text will be *bounded set* and *bounded*, respectively.

### Media

Media can be inserted using `[!M1234]` or `[Figure 1!M1243]`. Both examples will link to the media item "M1234", but the displayed link text will be *M1234* and *Figure 1*, respectively.

