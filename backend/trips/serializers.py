from rest_framework import serializers


class TripRequestSerializer(serializers.Serializer):
    current_location = serializers.CharField(required=True)
    pickup_location = serializers.CharField(required=True)
    dropoff_location = serializers.CharField(required=True)
    current_cycle_used = serializers.FloatField(required=True, min_value=0, max_value=70)
    
    carrier_name = serializers.CharField(required=False, allow_blank=True, default="")
    main_office_address = serializers.CharField(required=False, allow_blank=True, default="")
    home_terminal_address = serializers.CharField(required=False, allow_blank=True, default="")
    driver_name = serializers.CharField(required=False, allow_blank=True, default="")
    co_driver_name = serializers.CharField(required=False, allow_blank=True, default="")
    truck_tractor = serializers.CharField(required=False, allow_blank=True, default="")
    trailer = serializers.CharField(required=False, allow_blank=True, default="")
    dvl_manifest_no = serializers.CharField(required=False, allow_blank=True, default="")
    shipper_commodity = serializers.CharField(required=False, allow_blank=True, default="")
    timezone = serializers.CharField(required=False, default="UTC")

