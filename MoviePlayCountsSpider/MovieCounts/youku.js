function sign(e) {
            function t(e, t) {
                return e << t | e >>> 32 - t
            }
            function n(e, t) {
                var n, r, i, s, o;
                return i = 2147483648 & e,
                s = 2147483648 & t,
                n = 1073741824 & e,
                r = 1073741824 & t,
                o = (1073741823 & e) + (1073741823 & t),
                n & r ? 2147483648 ^ o ^ i ^ s : n | r ? 1073741824 & o ? 3221225472 ^ o ^ i ^ s : 1073741824 ^ o ^ i ^ s : o ^ i ^ s
            }
            function r(e, t, n) {
                return e & t | ~e & n
            }
            function i(e, t, n) {
                return e & n | t & ~n
            }
            function s(e, t, n) {
                return e ^ t ^ n
            }
            function o(e, t, n) {
                return t ^ (e | ~n)
            }
            function u(e, i, s, o, u, a, f) {
                return e = n(e, n(n(r(i, s, o), u), f)),
                n(t(e, a), i)
            }
            function a(e, r, s, o, u, a, f) {
                return e = n(e, n(n(i(r, s, o), u), f)),
                n(t(e, a), r)
            }
            function f(e, r, i, o, u, a, f) {
                return e = n(e, n(n(s(r, i, o), u), f)),
                n(t(e, a), r)
            }
            function l(e, r, i, s, u, a, f) {
                return e = n(e, n(n(o(r, i, s), u), f)),
                n(t(e, a), r)
            }
            function c(e) {
                for (var t, n = e.length, r = n + 8, i = (r - r % 64) / 64, s = 16 * (i + 1), o = new Array(s - 1), u = 0, a = 0; n > a; )
                    t = (a - a % 4) / 4,
                    u = a % 4 * 8,
                    o[t] = o[t] | e.charCodeAt(a) << u,
                    a++;
                return t = (a - a % 4) / 4,
                u = a % 4 * 8,
                o[t] = o[t] | 128 << u,
                o[s - 2] = n << 3,
                o[s - 1] = n >>> 29,
                o
            }
            function h(e) {
                var t, n, r = "", i = "";
                for (n = 0; 3 >= n; n++)
                    t = e >>> 8 * n & 255,
                    i = "0" + t.toString(16),
                    r += i.substr(i.length - 2, 2);
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
            var d, v, m, g, y, b, w, E, S, x = [], T = 7, N = 12, C = 17, k = 22, L = 5, A = 9, O = 14, M = 20, _ = 4, D = 11, P = 16, H = 23, B = 6, j = 10, F = 15, I = 21;
            for (e = p(e),
            x = c(e),
            b = 1732584193,
            w = 4023233417,
            E = 2562383102,
            S = 271733878,
            d = 0; d < x.length; d += 16)
                v = b,
                m = w,
                g = E,
                y = S,
                b = u(b, w, E, S, x[d + 0], T, 3614090360),
                S = u(S, b, w, E, x[d + 1], N, 3905402710),
                E = u(E, S, b, w, x[d + 2], C, 606105819),
                w = u(w, E, S, b, x[d + 3], k, 3250441966),
                b = u(b, w, E, S, x[d + 4], T, 4118548399),
                S = u(S, b, w, E, x[d + 5], N, 1200080426),
                E = u(E, S, b, w, x[d + 6], C, 2821735955),
                w = u(w, E, S, b, x[d + 7], k, 4249261313),
                b = u(b, w, E, S, x[d + 8], T, 1770035416),
                S = u(S, b, w, E, x[d + 9], N, 2336552879),
                E = u(E, S, b, w, x[d + 10], C, 4294925233),
                w = u(w, E, S, b, x[d + 11], k, 2304563134),
                b = u(b, w, E, S, x[d + 12], T, 1804603682),
                S = u(S, b, w, E, x[d + 13], N, 4254626195),
                E = u(E, S, b, w, x[d + 14], C, 2792965006),
                w = u(w, E, S, b, x[d + 15], k, 1236535329),
                b = a(b, w, E, S, x[d + 1], L, 4129170786),
                S = a(S, b, w, E, x[d + 6], A, 3225465664),
                E = a(E, S, b, w, x[d + 11], O, 643717713),
                w = a(w, E, S, b, x[d + 0], M, 3921069994),
                b = a(b, w, E, S, x[d + 5], L, 3593408605),
                S = a(S, b, w, E, x[d + 10], A, 38016083),
                E = a(E, S, b, w, x[d + 15], O, 3634488961),
                w = a(w, E, S, b, x[d + 4], M, 3889429448),
                b = a(b, w, E, S, x[d + 9], L, 568446438),
                S = a(S, b, w, E, x[d + 14], A, 3275163606),
                E = a(E, S, b, w, x[d + 3], O, 4107603335),
                w = a(w, E, S, b, x[d + 8], M, 1163531501),
                b = a(b, w, E, S, x[d + 13], L, 2850285829),
                S = a(S, b, w, E, x[d + 2], A, 4243563512),
                E = a(E, S, b, w, x[d + 7], O, 1735328473),
                w = a(w, E, S, b, x[d + 12], M, 2368359562),
                b = f(b, w, E, S, x[d + 5], _, 4294588738),
                S = f(S, b, w, E, x[d + 8], D, 2272392833),
                E = f(E, S, b, w, x[d + 11], P, 1839030562),
                w = f(w, E, S, b, x[d + 14], H, 4259657740),
                b = f(b, w, E, S, x[d + 1], _, 2763975236),
                S = f(S, b, w, E, x[d + 4], D, 1272893353),
                E = f(E, S, b, w, x[d + 7], P, 4139469664),
                w = f(w, E, S, b, x[d + 10], H, 3200236656),
                b = f(b, w, E, S, x[d + 13], _, 681279174),
                S = f(S, b, w, E, x[d + 0], D, 3936430074),
                E = f(E, S, b, w, x[d + 3], P, 3572445317),
                w = f(w, E, S, b, x[d + 6], H, 76029189),
                b = f(b, w, E, S, x[d + 9], _, 3654602809),
                S = f(S, b, w, E, x[d + 12], D, 3873151461),
                E = f(E, S, b, w, x[d + 15], P, 530742520),
                w = f(w, E, S, b, x[d + 2], H, 3299628645),
                b = l(b, w, E, S, x[d + 0], B, 4096336452),
                S = l(S, b, w, E, x[d + 7], j, 1126891415),
                E = l(E, S, b, w, x[d + 14], F, 2878612391),
                w = l(w, E, S, b, x[d + 5], I, 4237533241),
                b = l(b, w, E, S, x[d + 12], B, 1700485571),
                S = l(S, b, w, E, x[d + 3], j, 2399980690),
                E = l(E, S, b, w, x[d + 10], F, 4293915773),
                w = l(w, E, S, b, x[d + 1], I, 2240044497),
                b = l(b, w, E, S, x[d + 8], B, 1873313359),
                S = l(S, b, w, E, x[d + 15], j, 4264355552),
                E = l(E, S, b, w, x[d + 6], F, 2734768916),
                w = l(w, E, S, b, x[d + 13], I, 1309151649),
                b = l(b, w, E, S, x[d + 4], B, 4149444226),
                S = l(S, b, w, E, x[d + 11], j, 3174756917),
                E = l(E, S, b, w, x[d + 2], F, 718787259),
                w = l(w, E, S, b, x[d + 9], I, 3951481745),
                b = n(b, v),
                w = n(w, m),
                E = n(E, g),
                S = n(S, y);
            var q = h(b) + h(w) + h(E) + h(S);
            return q.toLowerCase()
        }