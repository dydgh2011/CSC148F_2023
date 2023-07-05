"""Locations for the simulation"""

from __future__ import annotations


class Location:
    """A two-dimensional location.

    Attributes:
    row: The row of location
    column: The column of location
    """
    row: int
    column: int

    def __init__(self, row: int, column: int) -> None:
        """Initialize a location.

        """
        self.row = row
        self.column = column

    def __str__(self) -> str:
        """Return a string representation.

        """
        return f"({self.row}, {self.column})"

    def __eq__(self, other: Location) -> bool:
        """Return True if self equals other, and false otherwise.

        """
        return self.row == other.row and self.column == other.column


def manhattan_distance(origin: Location, destination: Location) -> int:
    """Return the Manhattan distance between the origin and the destination.

    >>> origin = Location(2, 4)
    >>> destination = Location(5, 7)
    >>> manhattan_distance(origin, destination)
    6

    """

    x = abs(destination.row - origin.row)
    y = abs(destination.column - origin.column)
    return x + y


def deserialize_location(location_str: str) -> Location:
    """Deserialize a location.

    location_str: A location in the format 'row,col'
    """
    lst = location_str.split(",")
    x = int(lst[0])
    y = int(lst[1])
    return Location(x, y)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all()
    