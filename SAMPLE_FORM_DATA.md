# Sample Form Data for ELD Trip Planner

Copy and paste these values into the form:

## Required Fields (Must Fill)

**Current Location:**
```
Chicago, IL
```

**Pickup Location:**
```
Los Angeles, CA
```

**Dropoff Location:**
```
New York, NY
```

**Current Cycle Used (Hours):**
```
15.5
```

## Optional Fields

### Carrier Information

**Carrier Name:**
```
ABC Trucking Company
```

**Main Office Address:**
```
123 Main St, Chicago, IL 60601
```

**Home Terminal Address:**
```
456 Terminal Blvd, Chicago, IL 60601
```

**Driver Name:**
```
John Smith
```

**Co-Driver Name:**
```
Jane Doe
```

### Vehicle Information

**Truck/Tractor Number:**
```
TRK-12345
```

**Trailer Number:**
```
TRL-67890
```

### Shipping Information

**DVL/Manifest Number:**
```
DVL-2024-001234
```

**Shipper & Commodity:**
```
General Freight - Electronics
```

---

## Alternative: Use Browser Console

1. Open the browser console (F12 or Cmd+Option+I)
2. Go to the Console tab
3. Paste and run this code:

```javascript
// Fill form with sample data
const data = {
  current_location: "Chicago, IL",
  pickup_location: "Los Angeles, CA", 
  dropoff_location: "New York, NY",
  current_cycle_used: 15.5,
  carrier_name: "ABC Trucking Company",
  main_office_address: "123 Main St, Chicago, IL 60601",
  home_terminal_address: "456 Terminal Blvd, Chicago, IL 60601",
  driver_name: "John Smith",
  co_driver_name: "Jane Doe",
  truck_tractor: "TRK-12345",
  trailer: "TRL-67890",
  dvl_manifest_no: "DVL-2024-001234",
  shipper_commodity: "General Freight - Electronics"
};

document.querySelectorAll('input').forEach(input => {
  const name = input.name;
  if (data[name] !== undefined) {
    input.value = data[name];
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }
});
```



