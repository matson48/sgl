# add time and prev_time to SGL to allow "with sgl.at_fps(60):"
# 
# frame_dt = 1/fps
# if time > time_at_last_call + frame_dt: do()
# 
# keep track of time at last call with global dictionary for different
# frame rates

class Util():
    @staticmethod
    def lerp(start, end, time):
        # return start + time*(end - start)
        return (1-time)*start + time*end

class Easing():
    @staticmethod
    def linear(value):
        return value

    @staticmethod
    def ease_in(value):
        return value * value

    @staticmethod
    def ease_out(value):
        return value * (2-value)

class TweenManager():
    def __init__(self):
        self.tweens = []
        self.time = 0

    def add(self, tween):
        self.tweens.append(tween)
        return self.tweens[-1]

    def update(self, dt):
        self.time += dt

        for number, tween in enumerate(self.tweens):
            tween.update(dt)
            if tween.done: 
                tween.cheat()
                if tween.done_callback: tween.done_callback()
                if tween.bounce:
                    tween.reverse()
                else:
                    del self.tweens[number]

class Tween():
    def __init__(self, target, properties, duration, easing=Easing.linear, delay=0, bounce=False, done_callback=None):
        self.delay = delay
        self.duration = duration

        self.target = target
        self.originals = {key: getattr(target, key) for key in properties}
        self.destinations = properties

        self.easing_function = easing

        self.time = 0

        self.bounce = bounce
        self.done_callback = done_callback

        self.stopped = False

    @property
    def done(self):
        return (self.stopped or self.time > (self.delay + self.duration))

    def stop(self):
        self.stopped = True

    def cheat(self):
        for key in self.destinations:
            setattr(self.target, key, self.destinations[key])

        self.time = self.delay + self.duration + 1

    def reverse(self):
        self.originals, self.destinations = self.destinations, self.originals
        self.time = 0

    def update(self, dt):
        self.time += dt

        if self.time < self.delay: return

        # time = time elapsed/length
        time = (self.time-self.delay)/float(self.duration)

        for key in self.destinations:
            setattr(self.target, key, Util.lerp(
                self.originals[key],
                self.destinations[key],
                self.easing_function(time)
            ))

manager = TweenManager()

def to(target, properties, duration, easing=Easing.linear, delay=0, bounce=False, done_callback=None):
    return manager.add(Tween(target, properties, duration, easing, delay, bounce, done_callback))

# 'from' is a reserved word in Python |:(
def from_orig(target, properties, duration, easing=Easing.linear, delay=0, bounce=False, done_callback=None):
    originals = {key: getattr(target, key) for key in properties}

    for key in properties:
        setattr(target, key, properties[key])

    return manager.add(Tween(target, originals, duration, easing, delay, bounce, done_callback))

def update(dt):
    manager.update(dt)

if __name__ == "__main__":
    import sgl
    sgl.init(640, 480, 1)

    class p:
        x = 0 
        y = 0

    sgl.no_stroke()

    tw = None
    while sgl.is_running():
        sgl.clear(0)
        sgl.draw_circle(p.x, p.y, 20)

        if sgl.on_mouse_up():
            if tw: tw.stop()
            tw = to(p, {"x": sgl.get_mouse_x(), "y": sgl.get_mouse_y()}, 1, Easing.ease_out, bounce=True)

        update(sgl.get_dt())
        sgl.frame()
