import configparser as cp


class EscapeSeparatorInterpolation(cp.BasicInterpolation):
    def _interpolate_some(self, parser, option, accum, rest, section, map, depth):
        raw_val = parser.get(section, option, raw=True, fallback=rest)

        if depth > cp.MAX_INTERPOLATION_DEPTH:
            raise cp.InterpolationDepthError(option, section, raw_val)

        while rest:
            p = rest.find("%")

            if p < 0:
                accum.append(rest)
                return

            if p > 0:
                accum.append(rest[:p])
                rest = rest[p:]

            # p is no longer used
            c = rest[1:2]

            if c == "%":
                accum.append("%")
                rest = rest[2:]

            elif c != "(":
                rest = "%" + rest

            elif c == "(":
                m = self._KEYCRE.match(rest)
                if m is None:
                    raise cp.InterpolationSyntaxError(
                        option, section,
                        "bad interpolation variable reference %r" % rest
                    )

                var = parser.optionxform(m.group(1))
                rest = rest[m.end():]

                try:
                    v = map[var]
                except KeyError:
                    raise cp.InterpolationMissingOptionError(
                        option, section, raw_val, var
                    ) from None

                if "%" in v:
                    self._interpolate_some(
                        parser, option, accum, v,
                        section, map, depth + 1
                    )
                else:
                    accum.append(v)

            else:
                raise cp.InterpolationSyntaxError(
                    option, section,
                    "'%%' must be followed by '%%' or '(', found: %r" % (rest,)
                )
