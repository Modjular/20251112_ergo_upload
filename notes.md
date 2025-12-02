### 11/28/25
**Status**
 - `index.html` holds a nice 'uploading' component.
 - `canvas.html` handles tiling nicely
 - No actual tile-serving or pyramid-making yet.

**TODO**
 - Refactor `index.html` into a nice Vue component
 - Create a Vite server? (no, overkill at this point. Also why we don't need to refactor yet)
 - Pyramid-generation --> ChatGPT?


### 12/1/25
**Status**
 - Tiles load in `canvas`
 - Added endpoints for image metadata and tile retrieval
 - Opted to stick with single-file still. ~630 LoC is still pretty small
 - Added some fun buttons for 'Grid' and 'Fit all'

**Next Steps**
 - More stress testing with throttled speed
 - Gather a list of features. Do's AND dont's

### 12/2/25
For fun I asked ChatGPT Free, Gemini 3 Pro, and Amp Smart to refactor `canvas.html` to use pixi.js

Prompt:
```
I have a single file webapp.


Could you refactor it to utilize Pixi.JS?

...
```


 - ChatGPT didn't produce working code, but it's refactor looks a lot nicer and is shorter (440 loc)
 - Gemini 3 Pro produced the only working code, *and* heavily improved the loading and rendering. (600 loc)
 - Amp Smart Produced buggy code, but IMO better result than ChatGPT (582 loc)

I better benchmark would be a best-of-5 competition. But maybe Gemini is just better.