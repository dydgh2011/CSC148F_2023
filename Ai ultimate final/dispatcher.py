"""Dispatcher for the simulation"""

from typing import Optional
from driver import Driver
from rider import Rider


class Dispatcher:
    """A dispatcher fulfills requests from riders and drivers for a
    ride-sharing service.

    When a rider requests a driver, the dispatcher assigns a driver to the
    rider. If no driver is available, the rider is placed on a waiting
    list for the next available driver. A rider that has not yet been
    picked up by a driver may cancel their request.

    When a driver requests a rider, the dispatcher assigns a rider from
    the waiting list to the driver. If there is no rider on the waiting list
    the dispatcher does nothing. Once a driver requests a rider, the driver
    is registered with the dispatcher, and will be used to fulfill future
    rider requests.
    """
    _waiting_list_rider: list[Rider]
    _waiting_list_driver: list[Driver]

    def __init__(self) -> None:
        """Initialize a Dispatcher.

        """
        self._waiting_list_rider = []
        self._waiting_list_driver = []

    def __str__(self) -> str:
        """Return a string representation.

        """
        return f"The waiting list of drivers: {self._waiting_list_driver}," \
               f"riders: {self._waiting_list_rider}"

    def request_driver(self, rider: Rider) -> Optional[Driver]:
        """Return a driver for the rider, or None if no driver is available.

        Add the rider to the waiting list if there is no available driver.

        """
        if self._waiting_list_driver:
            min_time = None
            driver = None
            for i in self._waiting_list_driver:
                time = i.get_travel_time(rider.origin)
                if min_time is None or min_time > time:
                    min_time = time
                    driver = i
            self._waiting_list_driver.remove(driver)
            return driver
        else:
            self._waiting_list_rider.append(rider)
            return None

    def request_rider(self, driver: Driver) -> Optional[Rider]:
        """Return a rider for the driver, or None if no rider is available.

        If this is a new driver, register the driver for future rider requests.

        """
        if self._waiting_list_rider:
            rider = self._waiting_list_rider.pop(0)
            return rider
        else:
            self._waiting_list_driver.append(driver)
            return None

    def cancel_ride(self, rider: Rider) -> None:
        """Cancel the ride for rider.

        """
        if rider in self._waiting_list_rider:
            self._waiting_list_rider.remove(rider)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={'extra-imports': ['typing', 'driver', 'rider']})
