from config.config import cfg
from custom_shape.custom_load_shapes import CustomLoadShape

if cfg.webtours_base.included:
    from user_classes.wt_base_scenario import WebToursBaseUserClass
    WebToursBaseUserClass.weight = cfg.webtours_base.weight
if cfg.webtours_cancel.included:
    from user_classes.wt_cancel_scenario import WebToursCancelUserClass
    WebToursCancelUserClass.weight = cfg.webtours_cancel.weight