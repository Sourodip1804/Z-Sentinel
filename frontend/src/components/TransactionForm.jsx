import { useState } from "react"

const [form, setForm] = useState({
    amount: 1200,
    merchant_category: "online",
    device_novelty: 0,
    location_deviation: 0.2,
    transaction_velocity: 2,
    unusual_time: 0

})

onPredict({

    ...form,

    amount: Number(form.amount),

    device_novelty:
        Number(form.device_novelty),

    location_deviation:
        Number(form.location_deviation),

    transaction_velocity:
        Number(form.transaction_velocity),

    unusual_time:
        Number(form.unusual_time)

});