function  w(e) {
      "use strict";
        function i(e, t) {
            var n = (65535 & e) + (65535 & t);
            return (e >> 16) + (t >> 16) + (n >> 16) << 16 | 65535 & n
        }

        function a(e, t) {
            return e << t | e >>> 32 - t
        }

        function l(e, t, n, r, o, l) {
            return i(a(i(i(t, e), i(r, l)), o), n)
        }

        function u(e, t, n, r, o, i, a) {
            return l(t & n | ~t & r, e, t, o, i, a)
        }

        function s(e, t, n, r, o, i, a) {
            return l(t & r | n & ~r, e, t, o, i, a)
        }

        function c(e, t, n, r, o, i, a) {
            return l(t ^ n ^ r, e, t, o, i, a)
        }

        function f(e, t, n, r, o, i, a) {
            return l(n ^ (t | ~r), e, t, o, i, a)
        }

        function d(e, t) {
            e[t >> 5] |= 128 << t % 32, e[14 + (t + 64 >>> 9 << 4)] = t;
            var n, r, o, a, l, d = 1732584193, p = -271733879, h = -1732584194, m = 271733878;
            for (n = 0; n < e.length; n += 16)r = d, o = p, a = h, l = m, d = u(d, p, h, m, e[n], 7, -680876936), m = u(m, d, p, h, e[n + 1], 12, -389564586), h = u(h, m, d, p, e[n + 2], 17, 606105819), p = u(p, h, m, d, e[n + 3], 22, -1044525330), d = u(d, p, h, m, e[n + 4], 7, -176418897), m = u(m, d, p, h, e[n + 5], 12, 1200080426), h = u(h, m, d, p, e[n + 6], 17, -1473231341), p = u(p, h, m, d, e[n + 7], 22, -45705983), d = u(d, p, h, m, e[n + 8], 7, 1770035416), m = u(m, d, p, h, e[n + 9], 12, -1958414417), h = u(h, m, d, p, e[n + 10], 17, -42063), p = u(p, h, m, d, e[n + 11], 22, -1990404162), d = u(d, p, h, m, e[n + 12], 7, 1804603682), m = u(m, d, p, h, e[n + 13], 12, -40341101), h = u(h, m, d, p, e[n + 14], 17, -1502002290), p = u(p, h, m, d, e[n + 15], 22, 1236535329), d = s(d, p, h, m, e[n + 1], 5, -165796510), m = s(m, d, p, h, e[n + 6], 9, -1069501632), h = s(h, m, d, p, e[n + 11], 14, 643717713), p = s(p, h, m, d, e[n], 20, -373897302), d = s(d, p, h, m, e[n + 5], 5, -701558691), m = s(m, d, p, h, e[n + 10], 9, 38016083), h = s(h, m, d, p, e[n + 15], 14, -660478335), p = s(p, h, m, d, e[n + 4], 20, -405537848), d = s(d, p, h, m, e[n + 9], 5, 568446438), m = s(m, d, p, h, e[n + 14], 9, -1019803690), h = s(h, m, d, p, e[n + 3], 14, -187363961), p = s(p, h, m, d, e[n + 8], 20, 1163531501), d = s(d, p, h, m, e[n + 13], 5, -1444681467), m = s(m, d, p, h, e[n + 2], 9, -51403784), h = s(h, m, d, p, e[n + 7], 14, 1735328473), p = s(p, h, m, d, e[n + 12], 20, -1926607734), d = c(d, p, h, m, e[n + 5], 4, -378558), m = c(m, d, p, h, e[n + 8], 11, -2022574463), h = c(h, m, d, p, e[n + 11], 16, 1839030562), p = c(p, h, m, d, e[n + 14], 23, -35309556), d = c(d, p, h, m, e[n + 1], 4, -1530992060), m = c(m, d, p, h, e[n + 4], 11, 1272893353), h = c(h, m, d, p, e[n + 7], 16, -155497632), p = c(p, h, m, d, e[n + 10], 23, -1094730640), d = c(d, p, h, m, e[n + 13], 4, 681279174), m = c(m, d, p, h, e[n], 11, -358537222), h = c(h, m, d, p, e[n + 3], 16, -722521979), p = c(p, h, m, d, e[n + 6], 23, 76029189), d = c(d, p, h, m, e[n + 9], 4, -640364487), m = c(m, d, p, h, e[n + 12], 11, -421815835), h = c(h, m, d, p, e[n + 15], 16, 530742520), p = c(p, h, m, d, e[n + 2], 23, -995338651), d = f(d, p, h, m, e[n], 6, -198630844), m = f(m, d, p, h, e[n + 7], 10, 1126891415), h = f(h, m, d, p, e[n + 14], 15, -1416354905), p = f(p, h, m, d, e[n + 5], 21, -57434055), d = f(d, p, h, m, e[n + 12], 6, 1700485571), m = f(m, d, p, h, e[n + 3], 10, -1894986606), h = f(h, m, d, p, e[n + 10], 15, -1051523), p = f(p, h, m, d, e[n + 1], 21, -2054922799), d = f(d, p, h, m, e[n + 8], 6, 1873313359), m = f(m, d, p, h, e[n + 15], 10, -30611744), h = f(h, m, d, p, e[n + 6], 15, -1560198380), p = f(p, h, m, d, e[n + 13], 21, 1309151649), d = f(d, p, h, m, e[n + 4], 6, -145523070), m = f(m, d, p, h, e[n + 11], 10, -1120210379), h = f(h, m, d, p, e[n + 2], 15, 718787259), p = f(p, h, m, d, e[n + 9], 21, -343485551), d = i(d, r), p = i(p, o), h = i(h, a), m = i(m, l);
            return [d, p, h, m]
        }

        function p(e) {
            var t, n = "", r = 32 * e.length;
            for (t = 0; t < r; t += 8)n += String.fromCharCode(e[t >> 5] >>> t % 32 & 255);
            return n
        }

        function h(e) {
            var t, n = [];
            for (n[(e.length >> 2) - 1] = void 0, t = 0; t < n.length; t += 1)n[t] = 0;
            var r = 8 * e.length;
            for (t = 0; t < r; t += 8)n[t >> 5] |= (255 & e.charCodeAt(t / 8)) << t % 32;
            return n
        }

        function m(e) {
            return p(d(h(e), 8 * e.length))
        }


        function v(e) {
            var t, n, r = "0123456789abcdef", o = "";
            for (n = 0; n < e.length; n += 1)t = e.charCodeAt(n), o += r.charAt(t >>> 4 & 15) + r.charAt(15 & t);
            return o
        }

        function b(e) {
            return unescape(encodeURIComponent(e))
        }

        function g(e) {
            return m(b(e))
        }

        
            return v(g(e));
        }

//console.log(phantom.args[0]);
//console.log(phantom.args[1]);
i = new Date;
a = i.getTime();
l = 6e4 * i.getTimezoneOffset();
s = a + l;
c = 8;
f = s + 36e5 * c;
d = new Date(f);
p = d;
p = p.getDate() + 9 + 9 ^ 10;
p = w(String(p));
p = p.substring(0, 10);
p = w(p);
h = d.getDay() + 11397;
m = "/api/v/?z=" + p + "&jx=" + phantom.args[0] + "&s1ig=" + h + "&g=";
console.log(m);
phantom.exit(0);


