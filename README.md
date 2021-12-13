# PyRex – High-quality corpora from CommonCrawl snapshots

I stopped maintaining my old [texrex](https://github.com/rsling/texrex) web data cleaning software in December 2021. PyRex is a stream-linesd, cleaned up, and modular Python 3 reimplementation of texrex with a focus on analysing CommonCrawl data.

If things go well, NLP modules for German and English (such as currently available in [COWTek](https://github.com/rsling/cow)) might also be added, turning PyRex into a one-stop shop for turning CommonCrawl snapshots into usable high-quality German and English corpora.

I'm also planning to include some tools for crawl bias removal in PyRex based on the work I did for the ClaraX web crawler (part of texrex). This will only work if CommonCrawl data allow for a good guess of at least some properties of the web graph.

If you're a researcher interested in using/evaluating the kind of corpora that you can create with PyRex, visit [COW](https://www.webcorpora.org//), where we serve corpora created with PyRex's predecessor texrex.

# Planned Features

## Core processing

- WARC or ARC files
- strip HTML, scripts, stylesheets
- extract meta information from crawl headers
- normalize encodings to UTF-8 including repair strategies for messy encodings
- convert all HTML entities to appropriate codepoints (including rogue Win-1252)
- perform additional normalization (exotic Unicode)

## Cleanup (texrex re-implementation)

- filter perfect duplicate documents
- filter or mark near-duplicate documents
- filter or mark boilerplate passages ([Paper](http://rolandschaefer.net/?p=88))
- filter or mark in-document deduplication
- recognize the document language and assess the text quality ([Paper](http://rolandschaefer.net/?p=78))
- recognize block and sentence language (German and English)
- remove hard hyphenation (German and English)
- fix run-together sentences (German and English)

## Annotation, analysis and output (texrex re-implementation)

- add server IP geolocation meta information (country, region, city – currently based on GeoLite)
- link data/web graph analysis
- write standard-compliant XML output
- custom COCOA output format to bias restrictive intellectual property legislation ([Paper](http://rolandschaefer.net/?p=994))

## Future plans

- partial crawl bias removal based on crawling experiments ([Paper](http://rolandschaefer.net/?p=1201))
- full linguistic processing for German and English (from [COWTek](https://github.com/rsling/cow))

# Papers to read about PyRex (formerly texrex) and related technology

- http://rolandschaefer.net/?p=88
- http://rolandschaefer.net/?p=994
- http://rolandschaefer.net/?p=749
- http://rolandschaefer.net/?p=78
- http://rolandschaefer.net/?p=74
- http://rolandschaefer.net/?p=70

