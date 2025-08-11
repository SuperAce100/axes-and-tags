# Axes-and-Tags: LLM-Driven Design Galleries for Generative Content

![Axes-and-tags](/assets/hero.png)

Axes-and-Tags is a domain-agnostic framework that transforms abstract concepts into structured, interpretable design exploration. Instead of having to iterate on prompts endlessly, this system guides users through content generation one semantic dimension (or “axis”) at a time—like color scheme, object material, or tone of text. Each axis is explored via discrete, human-readable “tags” that ensure clarity, consistency, and control throughout the design process.

![Axes-and-tags User Interface](/assets/image.png)

## Adding a New Domain (`@domain.py`)

To add a new domain, all you'll need to do the required `generate_one` method in a subclass of `src/domains/domain.py`, specifying how your domain generates content from a concept and design space. You'll also need to write a quick JS method that given a HTML container will render the content you've generated!

We've pre-built the image, web, and text domains, which you can see in `src/domains`.



