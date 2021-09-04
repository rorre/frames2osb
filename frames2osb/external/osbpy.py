"""
MIT License

Copyright (c) 2017 Jiří Olszar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

--------------------

This is Wafu's osbpy, however I have reworked it to have static typing
and have rewritten parts of it to be more easily readable (hopefully)

Original repository is available here:
https://github.com/KawaiiWafu/osbpy
"""
import os
from typing import Iterable, List, Literal, Optional, Union
from frames2osb.external.typings import Origin, Layer, Loop, OsbEasing


def check_path(path: str):
    if not isinstance(path, str):
        raise ValueError("{val} is an invalid path.".format(val=path))
    return True


def check_layer(layer: Layer):
    if layer not in ("Background", "Fail", "Pass", "Foreground"):
        raise ValueError(
            "{val} is an invalid layer. ".format(val=layer)
            + "Valid values: Background, Fail, Pass, Foreground"
        )
    return True


def check_origin(origin: Origin):
    if origin not in (
        "TopLeft",
        "TopCentre",
        "TopRight",
        "CentreLeft",
        "Centre",
        "CentreRight",
        "BottomLeft",
        "BottomCentre",
        "BottomRight",
    ):
        raise ValueError("{val} is an invalid origin.".format(val=origin))
    return True


def check_easing(easing: OsbEasing):
    if easing not in [item.value for item in OsbEasing]:
        raise ValueError("{val} is an invalid easing.".format(val=easing))
    return True


def check_loop(loop: Loop):
    if loop not in ("LoopForever", "LoopOnce"):
        raise ValueError("{val} is an invalid loop type.".format(val=loop))
    return True


def check_float(dec: float):
    if not (isinstance(dec, int) or isinstance(dec, float)):
        raise TypeError("{val} is not a decimal or an integer.".format(val=dec))
    return True


def check_time(start: float, end: float) -> Literal[True]:
    if not (isinstance(start, float) or isinstance(start, int)):
        raise TypeError("Time {val} is not float.".format(val=start))

    if not (isinstance(end, float) or isinstance(end, int)):
        raise TypeError("Time {val} is not float.".format(val=end))

    if end < start:
        raise ValueError(
            "Start time {0} is greater than end time {1}.".format(start, end)
        )
    return True


def check_colours(args: Iterable[int]):
    for color in args:
        if color not in range(256):
            raise ValueError("{val} is an invalid color.".format(val=color))
    return True


def check_parameter(parameter: str):
    if parameter not in ("H", "V", "A"):
        raise ValueError("{val} is an invalid Parameter.".format(val=parameter))
    return True


def check_trigger(trigger: str):
    if trigger not in ("Failing", "Passing") and not trigger.startswith("HitSound"):
        raise ValueError(
            "{0} is an invalid Trigger. Valid: Failing, Passing, HitSound...".format(
                trigger
            )
        )
    return True


class Osbject:
    obj_background: List["Osbject"] = []
    obj_fail: List["Osbject"] = []
    obj_pass: List["Osbject"] = []
    obj_foreground: List["Osbject"] = []
    obj_link = {
        "Background": obj_background,
        "Fail": obj_fail,
        "Pass": obj_pass,
        "Foreground": obj_foreground,
    }

    _init = False

    def __init__(
        self,
        path: str,
        layer: Layer,
        origin: Origin,
        posx: float,
        posy: float,
        frame_count: Optional[int] = None,
        frame_rate: Optional[int] = None,
        loop: Optional[Loop] = None,
    ):
        Osbject.obj_link[layer].append(self)
        self.props: List[str] = []
        assert check_path(path) and check_layer(layer) and check_origin(origin)

        if frame_count and frame_rate and loop:
            tag = "Animation"
            assert (
                check_float(frame_count)
                and check_float(frame_rate)
                and check_loop(loop)
            )
            self.add(
                (
                    tag,
                    layer,
                    origin,
                    path,
                    posx,
                    posy,
                    frame_count,
                    frame_rate,
                    loop,
                )
            )
        else:
            tag = "Sprite"
            self.add((tag, layer, origin, path, posx, posy))

        self._init = True

    def add(self, args: Iterable[Union[str, float, OsbEasing]], loop=False):
        leading = ""
        if self._init:
            leading += " "

        if loop:
            leading += " "

        def _convert(v: Iterable[Union[str, float, OsbEasing]]):
            if isinstance(v, OsbEasing):
                return str(v.value)
            return str(v)

        props_string = leading + ",".join(map(_convert, args))
        self.props.append(props_string)

    def fade(
        self,
        easing: OsbEasing,
        start: float,
        end: float,
        start_fade: float,
        end_fade: float,
        loop: bool = False,
    ):
        assert (
            check_easing(easing)
            and check_time(start, end)
            and check_float(start_fade)
            and check_float(end_fade)
        )
        tag = "F"

        if start == end:
            end_time = ""
        else:
            end_time = str(end)

        if start_fade == end_fade:
            self.add((tag, easing, start, end_time, start_fade), loop)
        else:
            self.add((tag, easing, start, end_time, start_fade, end_fade), loop)

    def move(
        self,
        easing: OsbEasing,
        start: float,
        end: float,
        start_movex: float,
        start_movey: float,
        end_movex: float,
        end_movey: float,
        loop: bool = False,
    ):
        assert (
            check_float(start_movex)
            and check_float(start_movey)
            and check_float(end_movex)
            and check_float(end_movey)
            and check_easing(easing)
            and check_time(start, end)
        )
        tag = "M"

        if start == end:
            end_time = ""
        else:
            end_time = str(end)

        if start_movex == end_movex and start_movey == end_movey:
            self.add((tag, easing, start, end_time, start_movex, start_movey), loop)
        else:
            self.add(
                (
                    tag,
                    easing,
                    start,
                    end_time,
                    start_movex,
                    start_movey,
                    end_movex,
                    end_movey,
                ),
                loop,
            )

    def movex(
        self,
        easing: OsbEasing,
        start: float,
        end: float,
        start_movex: float,
        end_movex: float,
        loop: bool = False,
        swap: bool = False,
    ):
        assert (
            check_easing(easing)
            and check_time(start, end)
            and check_float(start_movex)
            and check_float(end_movex)
        )
        tag = "M" + "Y" if swap else "X"

        if start == end:
            end_time = ""
        else:
            end_time = str(end)

        if start_movex == end_movex:
            self.add((tag, easing, start, end_time, start_movex), loop)
        else:
            self.add((tag, easing, start, end_time, start_movex, end_movex), loop)

    def movey(
        self,
        easing: OsbEasing,
        start: float,
        end: float,
        start_movey: float,
        end_movey: float,
        loop: bool = False,
    ):
        self.movex(easing, start, end, start_movey, end_movey, loop, True)

    def scale(
        self,
        easing: OsbEasing,
        start: float,
        end: float,
        start_scale: float,
        end_scale: float,
        loop: bool = False,
    ):
        assert (
            check_easing(easing)
            and check_time(start, end)
            and check_float(start_scale)
            and check_float(end_scale)
        )
        tag = "S"

        if start == end:
            end_time = ""
        else:
            end_time = str(end)

        if start_scale == end_scale:
            self.add((tag, easing, start, end_time, start_scale), loop)
        else:
            self.add((tag, easing, start, end_time, start_scale, end_scale), loop)

    def vecscale(
        self,
        easing: OsbEasing,
        start: float,
        end: float,
        start_scalex: float,
        start_scaley: float,
        end_scalex: float,
        end_scaley: float,
        loop: bool = False,
    ):
        assert (
            check_float(start_scalex)
            and check_float(start_scaley)
            and check_float(end_scalex)
            and check_float(end_scaley)
            and check_easing(easing)
            and check_time(start, end)
        )
        tag = "V"

        if start == end:
            end_time = ""
        else:
            end_time = str(end)

        if start_scalex == end_scalex and start_scaley == end_scaley:
            self.add((tag, easing, start, end_time, start_scalex, start_scaley), loop)
        else:
            self.add(
                (
                    tag,
                    easing,
                    start,
                    end_time,
                    start_scalex,
                    start_scaley,
                    end_scalex,
                    end_scaley,
                ),
                loop,
            )

    def rotate(
        self,
        easing: OsbEasing,
        start: float,
        end: float,
        start_rotate: float,
        end_rotate: float,
        loop: bool = False,
    ):
        assert (
            check_easing(easing)
            and check_time(start, end)
            and check_float(start_rotate)
            and check_float(end_rotate)
        )
        tag = "R"

        if start == end:
            end_time = ""
        else:
            end_time = str(end)

        if start_rotate == end_rotate:
            self.add((tag, easing, start, end_time, start_rotate), loop)
        else:
            self.add((tag, easing, start, end_time, start_rotate, end_rotate), loop)

    def colour(
        self,
        easing: OsbEasing,
        start: float,
        end: float,
        r: int,
        g: int,
        b: int,
        end_r: int,
        end_g: int,
        end_b: int,
        loop: bool = False,
    ):
        assert (
            check_easing(easing)
            and check_time(start, end)
            and check_colours((r, g, b, end_r, end_g, end_b))
        )
        tag = "C"

        if start == end:
            end_time = ""
        else:
            end_time = str(end)

        if r == end_r and g == end_g and b == end_b:
            self.add((tag, easing, start, end_time, r, g, b), loop)
        else:
            self.add((tag, easing, start, end_time, r, g, b, end_r, end_g, end_b), loop)

    def para(self, easing: OsbEasing, start: float, end: float, parameter: str):
        assert (
            check_easing(easing)
            and check_time(start, end)
            and check_parameter(parameter)
        )
        tag = "P"
        if start == end:
            end_time = ""
        else:
            end_time = str(end)

        self.add((tag, easing, start, end_time, parameter))

    def loop(self, start: float, loop_count: int):
        assert check_float(start) and check_float(loop_count)

        tag = "L"
        self.add((tag, start, loop_count))

    def trigger(self, trigger: str, start: float, loop_count: int):
        assert check_trigger(trigger) and check_float(start) and check_float(loop_count)

        tag = "T"
        self.add((tag, trigger, start, loop_count))

    @classmethod
    def end(cls, osb_file):
        if os.path.isfile(osb_file):
            os.remove(osb_file)
        with open(osb_file, "a") as text:
            text.write(
                "[Events]\n//Background and Video events\n//Storyboard Layer 0 (Background)\n"
            )
            for val in cls.obj_background:
                text.write("%s\n" % "\n".join(val.props))
            text.write("//Storyboard Layer 1 (Fail)\n")
            for val in cls.obj_fail:
                text.write("%s\n" % "\n".join(val.props))
            text.write("//Storyboard Layer 2 (Pass)\n")
            for val in cls.obj_pass:
                text.write("%s\n" % "\n".join(val.props))
            text.write("//Storyboard Layer 3 (Foreground)\n")
            for val in cls.obj_foreground:
                text.write("%s\n" % "\n".join(val.props))
            text.write("//Storyboard Sound Samples\n")
