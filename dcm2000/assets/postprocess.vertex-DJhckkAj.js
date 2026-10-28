import{S as o}from"./index-DmjaE0dS.js";const e="postprocessVertexShader",s=`attribute vec2 position;uniform vec2 scale;varying vec2 vUV;const vec2 madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
vUV=(position*madd+madd)*scale;gl_Position=vec4(position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;o.ShadersStore[e]||(o.ShadersStore[e]=s);const i={name:e,shader:s};export{i as postprocessVertexShader};
