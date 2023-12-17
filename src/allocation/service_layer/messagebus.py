from typing import Union

from fastapi.logger import logger

from src.allocation.domain import events, commands
from src.allocation.service_layer import unit_of_work, handlers
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

Message = Union[commands.Command, events.Event]


def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)  # (2)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)  # (2)
            results.append(cmd_result)
        else:
            raise Exception(f"{message} was not an Event or Command")
    return results


def handle_event(
    event: events.Event,
    queue: list[Message],
    uow: unit_of_work.AbstractUnitOfWork,
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            for attempt in Retrying(
                stop=stop_after_attempt(3), wait=wait_exponential()
            ):
                with attempt:
                    logger.debug(f"handling event {event} with handler {handler}")
                    handler(event, uow=uow)
                    queue.extend(uow.collect_new_events())
        except RetryError as retry_failure:
            logger.error(
                f"Failed to handle event {retry_failure.last_attempt.attempt_number} times, giving up!"
            )
            continue


def handle_command(
    command: commands.Command,
    queue: list[Message],
    uow: unit_of_work.AbstractUnitOfWork,
):
    logger.debug("handling command %s", command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception("Exception handling command %s", command)
        raise


EVENT_HANDLERS: dict[type[events.Event], list[callable]] = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}

COMMAND_HANDLERS: dict[type[commands.Command], callable] = {
    commands.Allocate: handlers.allocate,
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}
