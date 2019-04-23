function c(e) {
    function t(e, t) {
        return e << t | e >>> 32 - t
    }
    function n(e, t) {
        var n, r, o, i, a;
        return o = 2147483648 & e,
            i = 2147483648 & t,
            n = 1073741824 & e,
            r = 1073741824 & t,
            a = (1073741823 & e) + (1073741823 & t),
            n & r ? 2147483648 ^ a ^ o ^ i : n | r ? 1073741824 & a ? 3221225472 ^ a ^ o ^ i : 1073741824 ^ a ^ o ^ i : a ^ o ^ i
    }
    function r(e, t, n) {
        return e & t | ~e & n
    }
    function o(e, t, n) {
        return e & n | t & ~n
    }
    function i(e, t, n) {
        return e ^ t ^ n
    }
    function a(e, t, n) {
        return t ^ (e | ~n)
    }
    function s(e, o, i, a, s, u, c) {
        return e = n(e, n(n(r(o, i, a), s), c)),
            n(t(e, u), o)
    }
    function u(e, r, i, a, s, u, c) {
        return e = n(e, n(n(o(r, i, a), s), c)),
            n(t(e, u), r)
    }
    function c(e, r, o, a, s, u, c) {
        return e = n(e, n(n(i(r, o, a), s), c)),
            n(t(e, u), r)
    }
    function l(e, r, o, i, s, u, c) {
        return e = n(e, n(n(a(r, o, i), s), c)),
            n(t(e, u), r)
    }
    function f(e) {
        for (var t, n = e.length, r = n + 8, o = (r - r % 64) / 64, i = 16 * (o + 1), a = new Array(i - 1), s = 0, u = 0; n > u;)
            t = (u - u % 4) / 4,
                s = u % 4 * 8,
                a[t] = a[t] | e.charCodeAt(u) << s,
                u++;
        return t = (u - u % 4) / 4,
            s = u % 4 * 8,
            a[t] = a[t] | 128 << s,
            a[i - 2] = n << 3,
            a[i - 1] = n >>> 29,
            a
    }
    function d(e) {
        var t, n, r = "", o = "";
        for (n = 0; 3 >= n; n++)
            t = e >>> 8 * n & 255,
                o = "0" + t.toString(16),
                r += o.substr(o.length - 2, 2);
        return r
    }
    function p(e) {
        e = e.replace(/\r\n/g, "\n");
        for (var t = "", n = 0; n < e.length; n++) {
            var r = e.charCodeAt(n);
            128 > r ? t += String.fromCharCode(r) : r > 127 && 2048 > r ? (t += String.fromCharCode(r >> 6 | 192),
                t += String.fromCharCode(63 & r | 128)) : (t += String.fromCharCode(r >> 12 | 224),
                    t += String.fromCharCode(r >> 6 & 63 | 128),
                    t += String.fromCharCode(63 & r | 128))
        }
        return t
    }

var h, g, v, m, y, _, w, b, O, S = [], x = 7, T = 12, E = 17, P = 22, C = 5, A = 9, k = 14, j = 20, L = 4, M = 11, R = 16, I = 23, N = 6, D = 10, q = 15, B = 21;
for (e = p(e),
    S = f(e),
    _ = 1732584193,
    w = 4023233417,
    b = 2562383102,
    O = 271733878,
    h = 0; h < S.length; h += 16)
    g = _,
        v = w,
        m = b,
        y = O,
        _ = s(_, w, b, O, S[h + 0], x, 3614090360),
        O = s(O, _, w, b, S[h + 1], T, 3905402710),
        b = s(b, O, _, w, S[h + 2], E, 606105819),
        w = s(w, b, O, _, S[h + 3], P, 3250441966),
        _ = s(_, w, b, O, S[h + 4], x, 4118548399),
        O = s(O, _, w, b, S[h + 5], T, 1200080426),
        b = s(b, O, _, w, S[h + 6], E, 2821735955),
        w = s(w, b, O, _, S[h + 7], P, 4249261313),
        _ = s(_, w, b, O, S[h + 8], x, 1770035416),
        O = s(O, _, w, b, S[h + 9], T, 2336552879),
        b = s(b, O, _, w, S[h + 10], E, 4294925233),
        w = s(w, b, O, _, S[h + 11], P, 2304563134),
        _ = s(_, w, b, O, S[h + 12], x, 1804603682),
        O = s(O, _, w, b, S[h + 13], T, 4254626195),
        b = s(b, O, _, w, S[h + 14], E, 2792965006),
        w = s(w, b, O, _, S[h + 15], P, 1236535329),
        _ = u(_, w, b, O, S[h + 1], C, 4129170786),
        O = u(O, _, w, b, S[h + 6], A, 3225465664),
        b = u(b, O, _, w, S[h + 11], k, 643717713),
        w = u(w, b, O, _, S[h + 0], j, 3921069994),
        _ = u(_, w, b, O, S[h + 5], C, 3593408605),
        O = u(O, _, w, b, S[h + 10], A, 38016083),
        b = u(b, O, _, w, S[h + 15], k, 3634488961),
        w = u(w, b, O, _, S[h + 4], j, 3889429448),
        _ = u(_, w, b, O, S[h + 9], C, 568446438),
        O = u(O, _, w, b, S[h + 14], A, 3275163606),
        b = u(b, O, _, w, S[h + 3], k, 4107603335),
        w = u(w, b, O, _, S[h + 8], j, 1163531501),
        _ = u(_, w, b, O, S[h + 13], C, 2850285829),
        O = u(O, _, w, b, S[h + 2], A, 4243563512),
        b = u(b, O, _, w, S[h + 7], k, 1735328473),
        w = u(w, b, O, _, S[h + 12], j, 2368359562),
        _ = c(_, w, b, O, S[h + 5], L, 4294588738),
        O = c(O, _, w, b, S[h + 8], M, 2272392833),
        b = c(b, O, _, w, S[h + 11], R, 1839030562),
        w = c(w, b, O, _, S[h + 14], I, 4259657740),
        _ = c(_, w, b, O, S[h + 1], L, 2763975236),
        O = c(O, _, w, b, S[h + 4], M, 1272893353),
        b = c(b, O, _, w, S[h + 7], R, 4139469664),
        w = c(w, b, O, _, S[h + 10], I, 3200236656),
        _ = c(_, w, b, O, S[h + 13], L, 681279174),
        O = c(O, _, w, b, S[h + 0], M, 3936430074),
        b = c(b, O, _, w, S[h + 3], R, 3572445317),
        w = c(w, b, O, _, S[h + 6], I, 76029189),
        _ = c(_, w, b, O, S[h + 9], L, 3654602809),
        O = c(O, _, w, b, S[h + 12], M, 3873151461),
        b = c(b, O, _, w, S[h + 15], R, 530742520),
        w = c(w, b, O, _, S[h + 2], I, 3299628645),
        _ = l(_, w, b, O, S[h + 0], N, 4096336452),
        O = l(O, _, w, b, S[h + 7], D, 1126891415),
        b = l(b, O, _, w, S[h + 14], q, 2878612391),
        w = l(w, b, O, _, S[h + 5], B, 4237533241),
        _ = l(_, w, b, O, S[h + 12], N, 1700485571),
        O = l(O, _, w, b, S[h + 3], D, 2399980690),
        b = l(b, O, _, w, S[h + 10], q, 4293915773),
        w = l(w, b, O, _, S[h + 1], B, 2240044497),
        _ = l(_, w, b, O, S[h + 8], N, 1873313359),
        O = l(O, _, w, b, S[h + 15], D, 4264355552),
        b = l(b, O, _, w, S[h + 6], q, 2734768916),
        w = l(w, b, O, _, S[h + 13], B, 1309151649),
        _ = l(_, w, b, O, S[h + 4], N, 4149444226),
        O = l(O, _, w, b, S[h + 11], D, 3174756917),
        b = l(b, O, _, w, S[h + 2], q, 718787259),
        w = l(w, b, O, _, S[h + 9], B, 3951481745),
        _ = n(_, g),
        w = n(w, v),
        b = n(b, m),
        O = n(O, y);
var F = d(_) + d(w) + d(b) + d(O);
return F.toLowerCase()
        }

