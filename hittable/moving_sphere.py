import taichi as ti
from vector import *
from . import empty_hit_record, set_face_normal
from material import Material
import ray


# struct for sphere
moving_sphere = ti.types.struct(center0=Point, center1=Point, radius=ti.f32, material=Material, t0=ti.f32, t1=ti.f32)


def MovingSphere(center0, center1, radius, material, t0, t1):
    return moving_sphere(center0=center0, center1=center1, radius=radius, material=material, t0=t0, t1=t1)


@ti.func
def center(sphere, t):
    return sphere.center0 + ((t - sphere.t0) / (sphere.t1 - sphere.t0)) * (sphere.center1 - sphere.center0)


@ti.func
def hit(sphere, r, t_min, t_max):
    ''' Intersect a ray with a given center and radius.
        Note we pass in the hit record by reference. '''
    hit = False
    rec = empty_hit_record()

    sphere_center = center(sphere, r.time)
    oc = r.orig - sphere_center
    a = r.dir.norm_sqr()
    half_b = oc.dot(r.dir)
    c = oc.norm_sqr() - sphere.radius ** 2

    discriminant = half_b ** 2 - a * c
    # check hit only if discriminint is > 0
    if discriminant >= 0.0:
        sqrtd = ti.sqrt(discriminant)
        root = (-half_b - sqrtd) / a
        hit = (root >= t_min and root < t_max)
        if not hit:
            root = (-half_b + sqrtd) / a
            hit = (root >= t_min and root < t_max)

        if hit:
            rec.t = root
            rec.p = ray.at(r, rec.t)
            outward_normal = (rec.p - sphere_center) / sphere.radius
            set_face_normal(r, outward_normal, rec)

    return hit, rec
