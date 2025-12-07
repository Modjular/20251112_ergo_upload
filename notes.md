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


### 12/6/25
Where are we?
 - Tiling works great, but now I think the next big push should be in the 'tile loading' experience.
    1. When panning, tiles load in logical order, but it would look better if they loaded in "nearest to the center of the screen" order.
    2. There's no queue or priority fetching, so panning really fast causes a ton of tiles to start fetching, and then pass out of view. I want the most important tiles to have priority over out-of-view tiles.
    3. If `L2_*` is fetching, but the lower res `L3_*` is available, that should be used as a placeholder until the `L2` is available.
    4. Currently, there is not cache eviction strategy, so memory growth is unchecked.


Wow, Gemini 3 Pro did a fantastic job implementing #3 (Painter's Algorithm)
Still need to implement priority queue (then base priority on distance from screen center).
Worry about cache eviction later.


Damn, Gemini keeps giving. It refactored the innefficient 'app.ticker' rendering loop into `requestRender` and covered all the cases where the canvas needs rerendering.

Can it implement my "resolution adjustment" request? I want to decouple the hard link between the internal `state.scale` and the current, requested tile-resolution. I still want it capped between 0 and 4. Basically, I don't mind seeing pixels on zoom. I think the current math is setup to ensure a literal 1-to-1 pixel ratio.

**Answer**
It can. It gave me all the right code, but I botched it by forgetting javascript doesn't do kwargs like python, so I ended up trying something like 'lodBias=0' which doesn't work, I think. 

TODO:
 - Global TileFetchManager for priority queuing
 - Prioritize tile fetching by distance-from-screen-center and Level
 - Limit concurrency so that higher-priority tiles can get into the queue
