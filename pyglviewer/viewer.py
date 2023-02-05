"""
    A simple fragment shader viewer
"""
import pyglet
import argparse
from pyglet.graphics.shader import Shader, ShaderProgram


VEXTEX_SHADER = """
#version 330

in vec2 position;
out vec2 surfacePosition;

void main() {
    gl_Position = vec4(position, 0, 1);
    surfacePosition = position;
}
"""


FRAGMENT_SHADER = """
#version 330

in vec2 surfacePosition;
out vec4 color;

uniform float time;
uniform vec2 resolution;
uniform vec2 mouse;

const float color_intensity = .5;
const float Pi = 3.14159;

void main() {
    float zoom = mouse.y * 3 + 2.3;
    mat2 rotScaleMat = zoom * mat2(cos(mouse.x), -sin(mouse.x), sin(mouse.x), cos(mouse.x));
    vec2 p = surfacePosition * vec2(1, resolution.y / resolution.x) * rotScaleMat;

    for(int i = 1; i < 5; i++) {
        vec2 newp = p;
        newp.x += .912 / float(i) * sin(float(i) * Pi * p.y + time * 0.15) + 0.91;
        newp.y += .913 / float(i) * cos(float(i) * Pi * p.x + time * -0.14) - 0.91;
        p=newp;
    }
    vec3 col = vec3((sin(p.x + p.y) * .91 + .1) * color_intensity);
    color = vec4(col, 1.0);
}
"""


class FragmentShaderGroup(pyglet.graphics.Group):
    def __init__(self, fragment_shader):
        super().__init__()
        self.shader_program = ShaderProgram(Shader(VEXTEX_SHADER, 'vertex'), Shader(fragment_shader, 'fragment'))
        self.cursor_position = (.0, .0)

    def set_state(self):
        self.shader_program.use()

    def unset_state(self):
        self.shader_program.stop()

    def update_time(self, dt: float):
        self.shader_program['time'] += dt

    def on_resize(self, width: int, height: int):
        self.shader_program['resolution'] = (width, height)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        hdx = float(dx) / float(self._window.screen.width)
        hdy = float(dy) / float(self._window.screen.height)
        self.cursor_position = (self.cursor_position[0] + hdx, self.cursor_position[1] + hdy)
        self.shader_program['mouse'] = self.cursor_position

    def register(self, window: pyglet.window.Window):
        self._window = window

        if 'time' in self.shader_program.uniforms:
            pyglet.clock.schedule_interval(self.update_time, 1.0 / 60.0)

        if 'resolution' in self.shader_program.uniforms:
            window.event(self.on_resize)

        if 'mouse' in self.shader_program.uniforms:
            window.set_exclusive_mouse(True)
            window.event(self.on_mouse_motion)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser("glviewer", description=__doc__)
    arg_parser.add_argument("-fs", "--fullscreen", dest="fullscreen", action='store_true')
    arg_parser.add_argument("-frag", "--fragmentShader", type=argparse.FileType('r'), dest="fragment_shader", help="Fragment shader file.")
    return arg_parser.parse_args()


def start():
    args = parse_args()
    fragment_shader = FRAGMENT_SHADER
    if args.fragment_shader:
        fragment_shader = args.fragment_shader.read()
        fragment_shader = f"#version 330\n{fragment_shader}"

    fragment_shader_group = FragmentShaderGroup(fragment_shader)

    window = pyglet.window.Window(resizable=True, caption="GlViewer", fullscreen=args.fullscreen)
    fragment_shader_group.register(window)

    batch = pyglet.graphics.Batch()
    vertex_list = fragment_shader_group.shader_program.vertex_list(4, pyglet.gl.GL_TRIANGLE_FAN, batch=batch, group=fragment_shader_group, position=('i', (1, 1, -1, 1, -1, -1, 1, -1)))

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()


if __name__ == "__main__":
    start()