class logger:
    def start_log(pygate, request_uuid):
            pygate.logger.info(request_uuid + " | ----- Start request ----- ")

    def end_log(pygate, request_uuid, start_time, status = "", before_out_time = 0):
        current_time = int(time.time() * 1000)
        if len(status) > 0:
            pygate.logger.info(request_uuid + " | Status: " + status)
        if before_out_time:
            pygate.logger.info(request_uuid + " | Time in gateway: " + str(before_out_time - start_time) + "ms")
            pygate.logger.info(request_uuid + " | API Backend time: " + str(current_time - before_out_time) + "ms")
        pygate.logger.info(request_uuid + " | Total response time: " + str(current_time - start_time) + "ms")
        pygate.logger.info(request_uuid + " | ----- End request ----- ")
