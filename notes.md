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