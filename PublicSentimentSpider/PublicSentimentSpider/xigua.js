function i() {
        var t = Math.floor((new Date).getTime() / 1e3)
          , e = t.toString(16).toUpperCase()

          , n = "6E148C47CD7B9F76399396297269E872";
        if (8 != e.length)
            return {
                as: "479BB4B7254C150",
                cp: "7E0AC8874BB0985"
            };
        for (var r = n.slice(0, 5), i = n.slice(-5), o = "", a = 0; a < 5; a++)
            o += r[a] + e[a];
        for (var u = "", l = 0; l < 5; l++)
            u += e[l + 3] + i[l];
        return {
            as: "A1" + o + e.slice(-3),
            cp: e.slice(0, 3) + u + "E1"
        }
    }

function C(t, e, n) {
            return e ? n ? w(e, t) : x(e, t) : n ? _(t) : b(t)
        }
function s(t, e) {
            return t << e | t >>> 32 - e
        }
function x(t, e) {
            return g(w(t, e))
        }
function g(t) {
            var e, n, r = "0123456789abcdef", i = "";
            for (n = 0; n < t.length; n += 1)
                e = t.charCodeAt(n),
                i += r.charAt(e >>> 4 & 15) + r.charAt(15 & e);
            return i
        }
function w(t, e) {
            return m(y(t), y(e))
        }
function m(t, e) {
            var n, r, i = h(t), o = [], s = [];
            for (o[15] = s[15] = void 0,
            i.length > 16 && (i = d(i, 8 * t.length)),
            n = 0; n < 16; n += 1)
                o[n] = 909522486 ^ i[n],
                s[n] = 1549556828 ^ i[n];
            return r = d(o.concat(h(e)), 512 + 8 * e.length),
            p(d(s.concat(r), 640))
        }
function y(t) {
            return unescape(encodeURIComponent(t))
        }
function h(t) {
            var e, n = [];
            for (n[(t.length >> 2) - 1] = void 0,
            e = 0; e < n.length; e += 1)
                n[e] = 0;
            for (e = 0; e < 8 * t.length; e += 8)
                n[e >> 5] |= (255 & t.charCodeAt(e / 8)) << e % 32;
            return n
        }
function d(t, e) {
            t[e >> 5] |= 128 << e % 32,
            t[(e + 64 >>> 9 << 4) + 14] = e;
            var n, r, i, s, a, d = 1732584193, p = -271733879, h = -1732584194, v = 271733878;
            for (n = 0; n < t.length; n += 16)
                r = d,
                i = p,
                s = h,
                a = v,
                d = u(d, p, h, v, t[n], 7, -680876936),
                v = u(v, d, p, h, t[n + 1], 12, -389564586),
                h = u(h, v, d, p, t[n + 2], 17, 606105819),
                p = u(p, h, v, d, t[n + 3], 22, -1044525330),
                d = u(d, p, h, v, t[n + 4], 7, -176418897),
                v = u(v, d, p, h, t[n + 5], 12, 1200080426),
                h = u(h, v, d, p, t[n + 6], 17, -1473231341),
                p = u(p, h, v, d, t[n + 7], 22, -45705983),
                d = u(d, p, h, v, t[n + 8], 7, 1770035416),
                v = u(v, d, p, h, t[n + 9], 12, -1958414417),
                h = u(h, v, d, p, t[n + 10], 17, -42063),
                p = u(p, h, v, d, t[n + 11], 22, -1990404162),
                d = u(d, p, h, v, t[n + 12], 7, 1804603682),
                v = u(v, d, p, h, t[n + 13], 12, -40341101),
                h = u(h, v, d, p, t[n + 14], 17, -1502002290),
                p = u(p, h, v, d, t[n + 15], 22, 1236535329),
                d = l(d, p, h, v, t[n + 1], 5, -165796510),
                v = l(v, d, p, h, t[n + 6], 9, -1069501632),
                h = l(h, v, d, p, t[n + 11], 14, 643717713),
                p = l(p, h, v, d, t[n], 20, -373897302),
                d = l(d, p, h, v, t[n + 5], 5, -701558691),
                v = l(v, d, p, h, t[n + 10], 9, 38016083),
                h = l(h, v, d, p, t[n + 15], 14, -660478335),
                p = l(p, h, v, d, t[n + 4], 20, -405537848),
                d = l(d, p, h, v, t[n + 9], 5, 568446438),
                v = l(v, d, p, h, t[n + 14], 9, -1019803690),
                h = l(h, v, d, p, t[n + 3], 14, -187363961),
                p = l(p, h, v, d, t[n + 8], 20, 1163531501),
                d = l(d, p, h, v, t[n + 13], 5, -1444681467),
                v = l(v, d, p, h, t[n + 2], 9, -51403784),
                h = l(h, v, d, p, t[n + 7], 14, 1735328473),
                p = l(p, h, v, d, t[n + 12], 20, -1926607734),
                d = c(d, p, h, v, t[n + 5], 4, -378558),
                v = c(v, d, p, h, t[n + 8], 11, -2022574463),
                h = c(h, v, d, p, t[n + 11], 16, 1839030562),
                p = c(p, h, v, d, t[n + 14], 23, -35309556),
                d = c(d, p, h, v, t[n + 1], 4, -1530992060),
                v = c(v, d, p, h, t[n + 4], 11, 1272893353),
                h = c(h, v, d, p, t[n + 7], 16, -155497632),
                p = c(p, h, v, d, t[n + 10], 23, -1094730640),
                d = c(d, p, h, v, t[n + 13], 4, 681279174),
                v = c(v, d, p, h, t[n], 11, -358537222),
                h = c(h, v, d, p, t[n + 3], 16, -722521979),
                p = c(p, h, v, d, t[n + 6], 23, 76029189),
                d = c(d, p, h, v, t[n + 9], 4, -640364487),
                v = c(v, d, p, h, t[n + 12], 11, -421815835),
                h = c(h, v, d, p, t[n + 15], 16, 530742520),
                p = c(p, h, v, d, t[n + 2], 23, -995338651),
                d = f(d, p, h, v, t[n], 6, -198630844),
                v = f(v, d, p, h, t[n + 7], 10, 1126891415),
                h = f(h, v, d, p, t[n + 14], 15, -1416354905),
                p = f(p, h, v, d, t[n + 5], 21, -57434055),
                d = f(d, p, h, v, t[n + 12], 6, 1700485571),
                v = f(v, d, p, h, t[n + 3], 10, -1894986606),
                h = f(h, v, d, p, t[n + 10], 15, -1051523),
                p = f(p, h, v, d, t[n + 1], 21, -2054922799),
                d = f(d, p, h, v, t[n + 8], 6, 1873313359),
                v = f(v, d, p, h, t[n + 15], 10, -30611744),
                h = f(h, v, d, p, t[n + 6], 15, -1560198380),
                p = f(p, h, v, d, t[n + 13], 21, 1309151649),
                d = f(d, p, h, v, t[n + 4], 6, -145523070),
                v = f(v, d, p, h, t[n + 11], 10, -1120210379),
                h = f(h, v, d, p, t[n + 2], 15, 718787259),
                p = f(p, h, v, d, t[n + 9], 21, -343485551),
                d = o(d, r),
                p = o(p, i),
                h = o(h, s),
                v = o(v, a);
            return [d, p, h, v]
        }

function u(t, e, n, r, i, o, s) {
    return a(e & n | ~e & r, t, e, i, o, s)
}
function a(t, e, n, r, i, a) {
            return o(s(o(o(e, t), o(r, a)), i), n)
        }
function o(t) {
        t = t || {};
        var e = t.successCb || function() {}
          , n = t.errorCb || function() {}
          , r = t.url || "/user/info/";
        (0,
        a.default)({
            url: r,
            method: "get",
            success: function(t) {
                var r = t || {};
                return "error" == r.message ? void n() : void e(r)
            },
            error: function() {
                n()
            }
        })
    }
function sign(t) {
                var e = (0,
                p.default)()
                  , n = 0;
                this.url = this._url,
                "refresh" === t ? (n = this.list.length > 0 ? this.list[0].behot_time : 0,
                this.url += "min_behot_time=" + n) : (n = this.list.length > 0 ? this.list[this.list.length - 1].behot_time : 0,
                this.url += "max_behot_time=" + n);
                var r = (0,
                m.sign)(n + "");
                (0,
                o.default)(this.params, {
                    as: e.as,
                    cp: e.cp,
                    _signature: r
                })
            }

function e() {
                        return r(e.y, arguments, k)
                    }

function r(e, a, r) {
        var n, t, s = {}, b = s.d = r ? r.d + 1 : 0;
         for (s["$" + b] = s,
        t = 0; t < b; t++)
            s[n = "$" + t] = r[n];
        for (t = 0,
        b = s.length = a.length; t < b; t++)
            s[t] = a[t];
        return c(e, 0, s)
    }