from datasette import hookimpl
import logging
@hookimpl
async def extra_template_vars(request, datasette):
    print("**********************  stuf here ***************")
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("***  plugin invoked ***")
    if request.path == "/":
        can_set_not_interested = await datasette.permission_allowed(
            request.actor,
            "set-not-interested",
            default=False
        )
        return {
            "can_set_not_interested": can_set_not_interested
        }
    return {}