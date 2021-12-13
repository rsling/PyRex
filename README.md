# PyRex – High-quality corpora from CommonCrawl snapshots

I stopped maintaining my old [texrex](https://github.com/rsling/texrex) web data cleaning software in December 2021. PyRex is a stream-lined, cleaned up, and modular Python 3 reimplementation of texrex with a focus on analysing CommonCrawl data. While focus is on (W)ARC and CommonCrawl, any source of web data can be processed at least in principle.

If things go well, NLP modules for German and English (such as currently available in [COWTek](https://github.com/rsling/cow)) might also be added, turning PyRex into a one-stop shop for turning CommonCrawl snapshots into usable and fully annotated high-quality German and English corpora.

I'm also planning to include modules which alleviate the intrinsic sampling bias of breadth-first crawls, based on the work I did for the ClaraX web crawler (part of texrex). However, this will only work if CommonCrawl data allow for a good guess of at least some properties of the real web graph.

If you're a researcher interested in using/evaluating the kind of corpora that you can create with PyRex, visit [COW](https://www.webcorpora.org/), where we serve corpora created with PyRex's predecessor texrex.

# Planned Features

### Core processing

- read WARC or ARC files
- strip HTML, scripts, stylesheets
- extract meta information from crawl headers
- normalize encodings to UTF-8 including repair strategies for messy encodings
- convert all HTML entities to appropriate codepoints (including rogue Win-1252)
- perform additional normalization (exotic Unicode)

### Cleanup (texrex re-implementation)

- filter perfect duplicate documents
- filter or mark near-duplicate documents
- filter or mark boilerplate passages ([Paper](http://rolandschaefer.net/?p=88))
- filter or mark in-document deduplication
- recognize the document language and assess the text quality ([Paper](http://rolandschaefer.net/?p=78))
- recognize block and sentence language (German and English)
- remove hard hyphenation (German and English)
- fix run-together sentences (German and English)

### Annotation, analysis and output (texrex re-implementation)

- add server IP geolocation meta information (country, region, city – currently based on GeoLite)
- link data/web graph analysis
- write standard-compliant XML output
- custom COCOA output format to bias restrictive intellectual property legislation ([Paper](http://rolandschaefer.net/?p=994))

### Future plans

- partial crawl bias removal based on crawling experiments ([Paper](http://rolandschaefer.net/?p=1201))
- full linguistic processing for German and English (from [COWTek](https://github.com/rsling/cow))

# Reasons for abandoning texrex and FreePascal

- There are many now obsolete low-level optimisations in texrex making the code unnecessarily complex.
- The thread pool implementation in texrex is quite messy.
- The FreePascal compiler is great, but the FreePascal ecosystem sucks.
- Python increases re-usability.

# Papers to read about PyRex (formerly texrex) and related technology

- http://rolandschaefer.net/?p=88
- http://rolandschaefer.net/?p=994
- http://rolandschaefer.net/?p=749
- http://rolandschaefer.net/?p=78
- http://rolandschaefer.net/?p=74
- http://rolandschaefer.net/?p=70


