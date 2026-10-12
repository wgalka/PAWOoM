from app.models import (
    Compartment,
    CompartmentCreate,
    CompartmentStatus,
    Locker,
    LockerCreate,
)


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class InMemoryStore:
    """Simple storage used only for the first laboratory."""

    ALLOWED_TRANSITIONS = {
        CompartmentStatus.FREE: {
            CompartmentStatus.RESERVED,
            CompartmentStatus.OUT_OF_SERVICE,
        },
        CompartmentStatus.RESERVED: {CompartmentStatus.OCCUPIED},
        CompartmentStatus.OCCUPIED: {CompartmentStatus.FREE},
        CompartmentStatus.OUT_OF_SERVICE: {CompartmentStatus.FREE},
    }

    def __init__(self) -> None:
        self.lockers: dict[str, Locker] = {}
        self.compartments: dict[str, Compartment] = {}
        self._seed()

    def _seed(self) -> None:
        locker = Locker(
            id="KRK-1024",
            name="Kraków Galeria",
            address="ul. Długa 10",
            city="Kraków",
        )
        self.lockers[locker.id] = locker
        self.compartments["KRK-1024-L1"] = Compartment(
            id="KRK-1024-L1",
            locker_id=locker.id,
            size="L",
        )
        self.compartments["KRK-1024-M1"] = Compartment(
            id="KRK-1024-M1",
            locker_id=locker.id,
            size="M",
        )

    def list_lockers(self) -> list[Locker]:
        return list(self.lockers.values())

    def get_locker(self, locker_id: str) -> Locker:
        try:
            return self.lockers[locker_id]
        except KeyError as exc:
            raise NotFoundError(f"Locker '{locker_id}' does not exist") from exc

    def add_locker(self, data: LockerCreate) -> Locker:
        if data.id in self.lockers:
            raise ConflictError(f"Locker '{data.id}' already exists")
        locker = Locker.model_validate(data.model_dump())
        self.lockers[locker.id] = locker
        return locker

    def list_compartments(self, locker_id: str) -> list[Compartment]:
        self.get_locker(locker_id)
        return [
            item for item in self.compartments.values() if item.locker_id == locker_id
        ]

    def add_compartment(
        self, locker_id: str, data: CompartmentCreate
    ) -> Compartment:
        self.get_locker(locker_id)
        if data.id in self.compartments:
            raise ConflictError(f"Compartment '{data.id}' already exists")
        compartment = Compartment(
            id=data.id,
            locker_id=locker_id,
            size=data.size,
        )
        self.compartments[compartment.id] = compartment
        return compartment

    def update_compartment_status(
        self, compartment_id: str, status: CompartmentStatus
    ) -> Compartment:
        try:
            compartment = self.compartments[compartment_id]
        except KeyError as exc:
            raise NotFoundError(
                f"Compartment '{compartment_id}' does not exist"
            ) from exc

        # Powtórne ustawienie tego samego statusu jest dozwolone.
        # Walidacja przejścia odbywa się przed modyfikacją magazynu.
        if status != compartment.status and status not in self.ALLOWED_TRANSITIONS[
            compartment.status
        ]:
            raise ConflictError(
                f"Cannot change compartment status from '{compartment.status.value}' "
                f"to '{status.value}'"
            )
        compartment.status = status
        return compartment
