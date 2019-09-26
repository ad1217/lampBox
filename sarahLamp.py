#!/usr/bin/env python3

from solid import *
from solid.utils import *
import math
import numpy as np

matThick = 3.4  # flat stock thickness
tabWidth = matThick
targetTabLength = 15
slop = 0.1 # a value to add to things to not have thin walls
wood_kerf = 0.13  # the amount the laser removes
acrylic_kerf = 0.11  # the amount the laser removes
cutout_margin = 3
cutout_page_margin = 3

class Box():
  def __init__(self, width, length, height, cutouts):
    self.width = width
    self.length = length
    self.height = height
    # sides = ["top", "left", "right", "front", "back", "top"]

    # TODO: allow setting enabled sides
    self.box_panels = {
      "top": self.panel(width, length, [0, 0, 0, 0], cutouts['top']),
      "left": self.panel(length, height, [-1, 1, 1, 1], cutouts['left']),
      "right": self.panel(length, height, [-1, 1, 1, 1], cutouts['right']),
      "front": self.panel(width, height, [-1, 1, 0, 0], cutouts['front']),
      "back": self.panel(width, height, [-1, 1, 0, 0], cutouts['back'])
    }

  def tabs(self, width, invert, inside=False):
    if invert < 0:
      return union()() # nop
    tabNum = math.ceil(width/targetTabLength)
    tabLength = width/(tabNum + (1 if tabNum % 2 == 0 else 0))
    start = tabLength if invert else 0
    return difference()(
      forward(wood_kerf if inside else 0)(square([width, tabWidth- (wood_kerf*2 if inside else wood_kerf)])),
      *[translate([xOffset - wood_kerf * 1.25/2, 0])(square([tabLength + wood_kerf * 1.25, tabWidth + wood_kerf * 2]))
       for xOffset in np.arange(start, width, tabLength * 2)])

  def panel_cutout(self, base, cutout):
    page = offset(delta=-matThick - cutout_page_margin)(base)
    background_cutout = intersection()(page, import_(cutout + "_background.svg"))
    acrylic_pieces = intersection()(import_(cutout + "_cutout.svg"))

    return union()(
      difference() (
        base,
        background_cutout,
        acrylic_pieces
      ),
      difference() (
        offset(cutout_margin)(
          acrylic_pieces
        ),
        debug(
          offset(-(wood_kerf + acrylic_kerf) / 2)(
            acrylic_pieces)))
    )

  def panel(self, width, length, invert_sides, cutout):
    return difference()(
      self.panel_cutout(square([width, length]), cutout),
      self.tabs(width, invert_sides[0]), # bottom
      forward(length)(mirror([0, 1])(self.tabs(width, invert_sides[1]))), # top
      rotate(90)(mirror([0, 1])(self.tabs(length, invert_sides[2]))), # left
      right(width)(rotate(90)(self.tabs(length, invert_sides[3]))), #right
    )

  @staticmethod
  def color_panels(panels):
    colors = {"top": "grey",
              "left": Green,
              "right": Magenta,
              "front": Yellow,
              "back": Red}
    return {k: color(colors[k])(v) for k, v in panels.items()}

  def panel_3d(self, panel):
    return linear_extrude(matThick)(panel)

  def to3d(self):
    panels = self.color_panels(
      {k: self.panel_3d(p) for k, p in self.box_panels.items()})

    return union()(
      up(self.height - matThick)(panels["top"]),
      forward(self.width)(rotate([90, 0, 90])(mirror([1,0,0])((panels["left"])))),
      forward(matThick)(rotate([90, 0, 0])(panels["front"])),
      right(self.width - matThick)(rotate([90, 0, 90])(panels["right"])),
      translate([self.width, self.length, 0])(rotate([90, 0, 0])(mirror([1,0,0])((panels["back"])))))

  def toFlat(self, separation=5):
    panels = self.color_panels(self.box_panels)

    return union()(
      panels["top"],
      left(self.width + separation)(panels["left"]),
      back(self.height + separation)(panels["front"]),
      right(self.width + separation)(panels["right"]),
      forward(self.length + separation)(panels["back"]))

  def toFlatStrip(self, separation=0.5):
    panels = self.color_panels(self.box_panels)

    return union()(
      panels["top"],
      right(self.width + separation)(panels["left"]),
      right((self.width + separation)*2)(panels["front"]),
      right((self.width + separation)*3)(panels["right"]),
      right((self.width + separation)*4)(panels["back"]))

cutouts = {
    "top": "drawing.dxf",
    "left": "lamp-091619",
    "right": "lamp-091619",
    "front": "lamp-091619",
    "back": "lamp-091619"
}

b = Box(150, 150, 200, cutouts)
scad_render_to_file(b.toFlat(), "laserBox.scad")
scad_render_to_file(b.toFlatStrip(), "laserBoxStrip.scad")
scad_render_to_file(b.to3d(), "laserBox3d.scad")
