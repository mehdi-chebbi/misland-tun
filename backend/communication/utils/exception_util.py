def process_exception(exception, do_print=True):
    import traceback
    import sys
    exc_info = sys.exc_info()
    msg = "-" * 30 + "Exception" + "-" * 50
    msg += "\n".join(traceback.format_exception(*(exc_info or sys.exc_info())))
    if do_print:
        print(msg)
    return msg