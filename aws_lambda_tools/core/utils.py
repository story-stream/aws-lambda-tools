def get_state_machine_name(arn):
    return arn.split(':')[-1]
