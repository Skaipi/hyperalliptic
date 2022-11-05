import pytest
from src.gf import GaloisField


def test_constructors():
    gf = GaloisField(11)

    assert gf.poly_zero == gf.poly([0]) and gf.poly_zero.deg == 0
    assert gf.poly_one == gf.poly([1]) and gf.poly_one.deg == 0
    assert gf.poly([1, 0, 0, 4]) == gf.poly([0, 0, 1, 0, 0, 4])
    assert gf.poly([3, 0, 1, 0, 2, 2]).deg == 5


def test_addition():
    gf = GaloisField(11)

    p1 = gf.poly([1, 0, 1, 8, 9, 7])
    p2 = gf.poly([1, 0, 3, 4])
    assert p1 + p2 == gf.poly([1, 0, 2, 8, 1, 0])


def test_substraction():
    gf = GaloisField(11)

    p1 = gf.poly([1, 0, 1, 8, 9, 7])
    p2 = gf.poly([1, 0, 3, 4])
    assert p2 - p1 == gf.poly([10, 0, 0, 3, 5, 8])
    assert p1 - p2 == gf.poly([1, 0, 0, 8, 6, 3])
    assert p1 - gf.poly_zero == p1
    assert p2 - gf.poly_zero == p2


def test_multiplication():
    gf = GaloisField(11)

    p1 = gf.poly([1, 0, 1, 8, 9, 7])
    p2 = gf.poly([1, 0, 3, 4])
    p3 = gf.poly([1, 0, 10])
    p4 = gf.poly([7, 9])
    assert p1 * p2 == gf.poly([1, 0, 4, 1, 1, 2, 4, 2, 6])
    assert p2 * p1 == gf.poly([1, 0, 4, 1, 1, 2, 4, 2, 6])
    assert p3 * p4 == gf.poly([7, 9, 4, 2])

    assert p1 * gf.poly_one == p1
    assert p2 * gf.poly_one == p2
    assert p3 * gf.poly_one == p3
    assert p4 * gf.poly_one == p4

    assert p1 * gf.poly_zero == gf.poly_zero
    assert p2 * gf.poly_zero == gf.poly_zero
    assert p3 * gf.poly_zero == gf.poly_zero
    assert p4 * gf.poly_zero == gf.poly_zero


def test_division():
    gf = GaloisField(11)

    p1 = gf.poly([1, 4, 2, 8, 1, 4])
    p2 = gf.poly([1, 4, 1, 4])
    p3 = gf.poly([1, 0, 1, 8, 9, 7])
    p4 = gf.poly([1, 0, 3, 4])
    p5 = gf.poly([1, 0, 10])
    p6 = gf.poly([7, 9])

    assert divmod(p1, p2) == (gf.poly([1, 0, 1]), gf.poly([0]))
    assert divmod(p3, p4) == (gf.poly([1, 0, 9]), gf.poly([4, 4, 4]))
    assert divmod(p5, p6) == (gf.poly([8, 7]), gf.poly([2]))

    assert p3 // p4 == gf.poly([1, 0, 9])
    assert p3 % p4 == gf.poly([4, 4, 4])

    assert p3 // gf.poly_one == p3
    assert p4 // gf.poly_one == p4
    assert p5 // gf.poly_one == p5
    assert p6 // gf.poly_one == p6

    with pytest.raises(ZeroDivisionError):
        p3 // gf.poly_zero

    with pytest.raises(ZeroDivisionError):
        p3 % gf.poly_zero


def test_comparison():
    gf = GaloisField(11)

    p1 = gf.poly([1, 0, 10])
    assert gf.poly_zero == 0
    assert gf.poly_one == 1
    assert p1 != 10


def test_exponentiation():
    gf = GaloisField(11)

    p1 = gf.poly([1, 0, 1])
    assert p1**2 == gf.poly([1, 0, 2, 0, 1])
    assert p1**3 == gf.poly([1, 0, 3, 0, 3, 0, 1])
    assert p1 * p1 * p1 * p1 == p1**4
    assert p1**0 == gf.poly_one


def test_to_string():
    gf = GaloisField(11)

    assert str(gf.poly_one) == "1"
    assert str(gf.poly_zero) == "0"
    assert str(gf.poly([1, 0, 3, 1, 1])) == "x^4 + 3x^2 + x + 1"
    assert str(gf.poly([1, 0, 3, 1, 0])) == "x^4 + 3x^2 + x"
    assert (
        str(
            gf.poly(
                [gf.poly([1, 0, 3, 1, 1]), gf.poly([1, 0, 3, 1, 0]), gf.poly([0])], "y"
            )
        )
        == "(x^4 + 3x^2 + x + 1)y^2 + (x^4 + 3x^2 + x)y"
    )


def test_derivative():
    gf = GaloisField(11)

    p1 = gf.poly([1, 0, 1, 8, 9, 7])
    p2 = gf.poly([1, 0, 3, 4])
    p3 = gf.poly([1, 0, 10])
    p4 = gf.poly([7, 9])
    p5 = gf.poly([4])

    assert p1.derivative() == gf.poly([5, 0, 3, 5, 9])
    assert p2.derivative() == gf.poly([3, 0, 3])
    assert p3.derivative() == gf.poly([2, 0])
    assert p4.derivative() == gf.poly([7])
    assert p5.derivative() == gf.poly_zero


def test_gcd():
    gf = GaloisField(11)

    p1 = gf.poly([1, 7, 6])
    p2 = gf.poly([1, 6, 5])

    p3 = gf.poly([1, 4, 1, 4])
    p4 = gf.poly([1, 0, 1])

    assert p1.gcd(p2) == gf.poly([1, 1])
    assert p3.gcd(p4) == p4


def test_factorization():
    gf = GaloisField(11)

    p1 = gf.poly([1, 0, 1])
    p2 = gf.poly([1, 4])
    p3 = gf.poly([1, 1, 3])

    p = p1**3 * p2**2
    factors = p.factor()

    p1_multiplicity = 0
    p2_multiplicity = 0
    for f in factors:
        if f == p1:
            p1_multiplicity += 1
        if f == p2:
            p2_multiplicity += 1

    assert p1_multiplicity == 3
    assert p2_multiplicity == 2
    assert len(p3.factor()) == 2 and gf.poly([1, 6]) in p3.factor()


def test_irreducibility():
    gf = GaloisField(2)

    poly = gf.poly([1, 0, 0, 0, 1, 1, 1, 0, 1])
    assert poly.is_irreducible() == True

    poly = gf.poly([1, 0, 0, 0, 1, 1, 0, 1, 1])
    assert poly.is_irreducible() == True

    poly = gf.poly([1, 0, 1, 0, 1, 0, 0, 0])
    assert poly.is_irreducible() == False

    gf = GaloisField(7)
    poly = gf.poly([1, 6, 1, 3, 0, 6, 5])
    assert poly.is_irreducible() == False
