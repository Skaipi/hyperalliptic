from src.integer import ZP
from src.utils import gf_operation
from random import randint


INF_POINT = ("Inf", "Inf")


class HC:
    def __init__(self, gf, h, f):
        self.g = f.deg // 2
        self.gf = gf
        self.h = h
        self.f = f

        if f.coeff[0] != 1:
            raise ValueError("Function f must be monic")
        if f.deg % 2 == 0:
            raise ValueError("Degree of function f must be an odd number")
        if h.deg > self.g:
            raise ValueError("Invalid function h for Curve of given genus")
        if gf.p != 2 and h != 0:
            raise ValueError("h(x) must be 0 for char(F) != 2")

        # TODO:
        # Check if C is smooth

    def divisor(self, a, b):
        return Divisor(self, a, b)

    def zero_divisor(self):
        return Divisor.zero(self)

    def divisor_from_points(self, points):
        return Divisor.from_points(self, points)

    def get_random_divisor(self):
        points = []
        for i in range(self.g):
            p = self.get_random_point()
            while self.point_inverse(p) in points:
                p = self.get_random_point()
            points.append(p)
        return Divisor.from_points(self, points)

    def get_random_point(self):
        point = None
        while point == None:
            x = randint(0, self.gf.p)
            point = self._point_from_x(x) if x != self.gf.p else INF_POINT
        return point

    def point_inverse(self, point):
        if point == INF_POINT:
            return point
        x, y = point[0], point[1]
        return (x, -y - self.h(x))

    def _x_from_points(self, points):
        return list(map(lambda p: p[0], points))

    def _y_from_points(self, points):
        return list(map(lambda p: p[1], points))

    def _point_from_x(self, x):
        # NOTE: This formula works for fields of characteristic != 2 (regular quadratic equation solution might not work)
        hx = self.h(x)
        fx = self.f(x)
        discriminant = hx * hx + 4 * fx
        if not discriminant.is_quadratic_residue():
            return None
        y1 = (-hx + self.gf.sqrt(discriminant)) / self.gf(2)
        y2 = -y1 - hx
        y = y1 if randint(0, 1) == 0 else y2
        return (x, y)

    def get_all_points(self):
        result = [INF_POINT]
        for x in self.gf.get_elements():
            point = self._point_from_x(x)
            if point == None:
                continue
            result.append(point)
            result.append(self.point_inverse(point))
        return result

    def __str__(self):
        return f"C: y^2 + ({str(self.h)})y = {str(self.f)}"


class Divisor:
    def __init__(self, curve, poly_u, poly_v):
        # Mumford representation as pair of polynomials a, b
        # a | b^2 + bh - f && deg(b) < deg(a) <= genus
        self.c = curve
        self.gf = self.c.gf
        self.u = poly_u
        self.v = poly_v

    @staticmethod
    def from_points(curve, points):
        # Find first polynomial of Mumford representation
        valid_points = list(filter(lambda p: p != INF_POINT, points))
        gf = curve.gf
        u = gf.poly_one
        for x in curve._x_from_points(valid_points):
            u *= gf.poly([gf(1), -x])

        valid_unique_points = list(set(valid_points))
        p_x = curve._x_from_points(valid_unique_points)
        p_y = curve._y_from_points(valid_unique_points)

        # Find second polynomial via Lagrange interpolation
        v = gf.poly_zero
        for i in range(len(p_y)):
            tmp = gf.poly_one
            for j in range(len(p_x)):
                if j == i:
                    continue
                tmp *= gf.poly([gf(1), -p_x[j]]) / (p_x[i] - p_x[j])
            v += tmp * p_y[i]

        return Divisor(curve, u, v)

    @classmethod
    def zero(cls, curve):
        return Divisor(curve, curve.gf.poly_one, curve.gf.poly_zero)

    @property
    def points(self):
        if hasattr(self, "_points"):
            return self._points

        c, u, v = self.c, self.u, self.v
        u_factors = u.factors()
        if len(u_factors) < c.g:
            raise ValueError("Divisor has non F-rational points in supp")
        roots = [-factor.coeff[-1] for factor in u_factors]
        points = [c._point_from_x(root) for root in roots]
        valid_points = [p if v(p[0]) == p[1] else c.point_inverse(p) for p in points]
        # fill missing g-tuple entries with infinity points
        valid_points += [INF_POINT] * (c.g - len(valid_points))
        self._points = valid_points
        return valid_points

    def to_reduced(self):
        u, v, f, h, g = self.u, self.v, self.c.f, self.c.h, self.c.g

        _u = (f - v * h - v * v) // u
        _v = (-h - v) % _u
        while _u.deg > g:
            _u = (f - v * h - v * v) // _u
            _v = (-h - v) % _u

        _u = _u.to_monic()

        return Divisor(self.c, _u, _v)

    @gf_operation
    def __add__(self, other):
        if self == Divisor.zero(self.c):
            return other
        if other == Divisor.zero(self.c):
            return self

        u1, u2, v1, v2 = self.u, other.u, self.v, other.v
        d1, e1, e2 = u1.xgcd(u2)
        d, c1, c2 = d1.xgcd(v1 + v2 + self.c.h)
        s1 = c1 * e1
        s2 = c1 * e2
        s3 = c2
        u = (u1 * u2) // d**2
        v = ((s1 * u1 * v2 + s2 * u2 * v1 + s3 * (v1 * v2 + self.c.f)) // d) % u

        return Divisor(self.c, u, v).to_reduced()

    def __mul__(self, other):
        if not isinstance(other, int) and not isinstance(other, ZP):
            raise ValueError(f"Divisor cannot be multiplied by {other}")

        tmp = self
        exp = other if isinstance(other, int) else other.value
        result = Divisor.zero(self.c)

        while exp:
            if exp % 2 == 1:
                result += tmp
            tmp += tmp
            exp = exp // 2
        return result

    def __neg__(self):
        b = -self.v - self.c.h
        return Divisor(self.c, self.u, b)

    def __eq__(self, other):
        if isinstance(other, Divisor):
            return self.u == other.u and self.v == other.v
        return False

    def __str__(self):
        return f"D: {str(self.u)} | {str(self.v)}"

    def __repr__(self):
        return str(self)
