/**
 * Created by HUANGD on 2021/10/4.
 */


var r, h = 0, d = 0;
var i = 0
    , b = []
    , f
    , v;
var m = new Uint8Array(16);
//console.log("begin crypto");
window.crypto.getRandomValues(m);
/*for(var i4=0;i4<m.length;i4++)
{
   console.log("m["+i4+"]: "+m[i4]);
}*/

f = r = [1 | m[0], m[1], m[2], m[3], m[4], m[5]];
v = 16383 & (m[6] << 8 | m[7]);

var y = (new Date).getTime()
    , w = d + 1
    , dt = y - h + (w - d) / 1e4;
if (dt < 0 && (v = v + 1 & 16383),
    (dt < 0 || y > h) && (w = 0),
    w >= 1e4)
{
    //console.log("throw new Error");
    throw new Error("uuid.v1(): Can't create more than 10M uuids/sec");
}

h = y;
d = w;


var x = (1e4 * (268435455 & (y += 122192928e5)) + w) % 4294967296;
//console.log("compute x="+x);
b[i++] = x >>> 24 & 255,
    b[i++] = x >>> 16 & 255,
    b[i++] = x >>> 8 & 255,
    b[i++] = 255 & x;
var _ = y / 4294967296 * 1e4 & 268435455;
//console.log("compute _="+_);
b[i++] = _ >>> 8 & 255,
    b[i++] = 255 & _,
    b[i++] = _ >>> 24 & 15 | 16,
    b[i++] = _ >>> 16 & 255,
    b[i++] = v >>> 8 | 128,
    b[i++] = 255 & v;
for (var A = 0; A < 6; ++A)
    b[i + A] = f[A];
/*for( i4=0;i4<b.length;i4++)
{
   console.log("b["+i4+"]: "+b[i4]);
}
console.log("compute _="+_);*/
for (var n = [], i2 = 0; i2 < 256; ++i2) {
    n[i2] = (i2 + 256).toString(16).substr(1);
    //console.log("compute n[" + i2 + "]: " + n[i2]);
}

/*console.log("end compute n: ");
for( i4=0;i4<n.length;i4++)
{
   console.log("n["+i4+"]: "+n[i4]);
}*/
var i3 = 0;
var result = [n[b[i3++]], n[b[i3++]], n[b[i3++]], n[b[i3++]], "-", n[b[i3++]], n[b[i3++]], "-", n[b[i3++]], n[b[i3++]], "-", n[b[i3++]], n[b[i3++]], "-", n[b[i3++]], n[b[i3++]], n[b[i3++]], n[b[i3++]], n[b[i3++]], n[b[i3++]]].join("");
console.log([y.toString(), result].join(" "));
phantom.exit();