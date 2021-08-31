import os
from typing import Iterable, List, Literal, Optional

Origin = Literal[
    "TopLeft",
    "TopCentre",
    "TopRight",
    "CentreLeft",
    "Centre",
    "CentreRight",
    "BottomLeft",
    "BottomCentre",
    "BottomRight",
]
Layer = Literal["Background", "Fail", "Pass", "Foreground"]
Loop = Literal["LoopForever", "LoopOnce"]


def check_path(path: str):
    if type(path) is not str:
        print("{val} is an invalid path.".format(val=path))
        return False
    return True


def check_layer(layer: Layer):
    if layer not in ("Background", "Fail", "Pass", "Foreground"):
        print(
            "{val} is an invalid layer. Valid: Background, Fail, Pass, Foreground".format(
                val=layer
            )
        )
        return False
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
        print(
            "{val} is an invalid origin. Valid: TopLeft, TopCentre, TopRight, CentreLeft, Centre, CentreRight,"
            "BottomLeft, BottomCentre, BottomRight".format(val=origin)
        )
        return False
    return True


def check_easing(easing: int):
    if easing not in range(35):
        print("{val} is an invalid easing. Valid: Integers 0 - 34".format(val=easing))
        return False
    return True


def check_loop(loop: Loop):
    if loop not in ("LoopForever", "LoopOnce"):
        print(
            "{val} is an invalid loop type. Valid: LoopForever, LoopOnce".format(
                val=loop
            )
        )
        return False
    return True


def check_float(dec: float):
    if not (isinstance(dec, int) or isinstance(dec, float)):
        print("{val} is not a decimal or an integer.".format(val=dec))
        return False
    return True


def check_time(start: float, end: float):
    if not (isinstance(start, float) or isinstance(start, int)):
        print("Time {val} is not float.".format(val=start))
        return False
    if not (isinstance(end, float) or isinstance(end, int)):
        print("Time {val} is not float.".format(val=end))
        return False

    if end < start:
        print(
            "End time {val1} is greater than start time {val2}.".format(
                val1=end, val2=start
            )
        )
        return False
    return True


def check_colours(args: Iterable[int]):
    for color in args:
        if color not in range(256):
            print("{val} is an invalid color. Valid: 0 - 255".format(val=color))
            return False
    return True


def check_parameter(parameter: str):
    if parameter not in ("H", "V", "A"):
        print("{val} is an invalid Parameter. Valid: H, V, A".format(val=parameter))
        return False
    return True


def check_trigger(trigger: str):
    if trigger not in ("Failing", "Passing") and not trigger.startswith("HitSound"):
        print(
            "{val} is an invalid Trigger. Valid: Failing, Passing, HitSound...".format(
                val=trigger
            )
        )
        return False
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

    def add(self, args: Iterable):
        self.props.append(",".join(map(str, args)))

    def fade(
        self,
        easing: int,
        start: float,
        end: float,
        start_fade: float,
        end_fade: float,
        loop: Optional[bool] = False,
    ):
        assert (
            check_easing(easing)
            and check_time(start, end)
            and check_float(start_fade)
            and check_float(end_fade)
        )

        if start == end:
            end = ""

        if loop:
            tag = "\n  F"
        else:
            tag = "\n F"

        if start_fade == end_fade:
            self.add((tag, easing, start, end, start_fade))
        else:
            self.add((tag, easing, start, end, start_fade, end_fade))

    def move(
        self,
        easing: int,
        start: float,
        end: float,
        start_movex: float,
        start_movey: float,
        end_movex: float,
        end_movey: float,
        loop: Optional[bool] = False,
    ):
        assert (
            check_float(start_movex)
            and check_float(start_movey)
            and check_float(end_movex)
            and check_float(end_movey)
            and check_easing(easing)
            and check_time(start, end)
        )

        if start == end:
            end = ""

        if loop:
            tag = "\n  M"
        else:
            tag = "\n M"

        if start_movex == end_movex and start_movey == end_movey:
            self.add((tag, easing, start, end, start_movex, start_movey))
        else:
            self.add(
                (
                    tag,
                    easing,
                    start,
                    end,
                    start_movex,
                    start_movey,
                    end_movex,
                    end_movey,
                )
            )

    def movex(
        self,
        easing: int,
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

        if start == end:
            end = ""

        if loop:
            if swap:
                tag = "\n  MY"
            else:
                tag = "\n  MX"
        else:
            if swap:
                tag = "\n MY"
            else:
                tag = "\n MX"

        if start_movex == end_movex:
            self.add((tag, easing, start, end, start_movex))
        else:
            self.add((tag, easing, start, end, start_movex, end_movex))

    def movey(
        self,
        easing: int,
        start: float,
        end: float,
        start_movey: float,
        end_movey: float,
        loop: bool = False,
    ):
        self.movex(easing, start, end, start_movey, end_movey, loop, True)

    def scale(
        self,
        easing: int,
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
        if start == end:
            end = ""

        if loop:
            tag = "\n  S"
        else:
            tag = "\n S"

        if start_scale == end_scale:
            self.add((tag, easing, start, end, start_scale))
        else:
            self.add((tag, easing, start, end, start_scale, end_scale))

    def vecscale(
        self,
        easing: int,
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

        if start == end:
            end = ""

        if loop:
            tag = "\n  V"
        else:
            tag = "\n V"

        if start_scalex == end_scalex and start_scaley == end_scaley:
            self.add((tag, easing, start, end, start_scalex, start_scaley))
        else:
            self.add(
                (
                    tag,
                    easing,
                    start,
                    end,
                    start_scalex,
                    start_scaley,
                    end_scalex,
                    end_scaley,
                )
            )

    def rotate(
        self,
        easing: int,
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
        if start == end:
            end = ""

        if loop:
            tag = "\n  R"
        else:
            tag = "\n R"

        if start_rotate == end_rotate:
            self.add((tag, easing, start, end, start_rotate))
        else:
            self.add((tag, easing, start, end, start_rotate, end_rotate))

    def colour(
        self,
        easing: int,
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
        if start == end:
            end = ""

        if loop:
            tag = "\n  C"
        else:
            tag = "\n C"

        if r == end_r and g == end_g and b == end_b:
            self.add((tag, easing, start, end, r, g, b))
        else:
            self.add((tag, easing, start, end, r, g, b, end_r, end_g, end_b))

    def para(self, easing: int, start: float, end: float, parameter: str):
        assert (
            check_easing(easing)
            and check_time(start, end)
            and check_parameter(parameter)
        )
        if start == end:
            end = ""

        tag = "\n P"
        self.add((tag, easing, start, end, parameter))

    def loop(self, start: float, loop_count: int):
        assert check_float(start) and check_float(loop_count)

        tag = "\n L"
        self.add((tag, start, loop_count))

    def trigger(self, trigger: str, start: float, loop_count: int):
        assert check_trigger(trigger) and check_float(start) and check_float(loop_count)

        tag = "\n T"
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
                text.write("%s\n" % "".join(val.props))
            text.write("//Storyboard Layer 1 (Fail)\n")
            for val in cls.obj_fail:
                text.write("%s\n" % "".join(val.props))
            text.write("//Storyboard Layer 2 (Pass)\n")
            for val in cls.obj_pass:
                text.write("%s\n" % "".join(val.props))
            text.write("//Storyboard Layer 3 (Foreground)\n")
            for val in cls.obj_foreground:
                text.write("%s\n" % "".join(val.props))
            text.write("//Storyboard Sound Samples\n")
