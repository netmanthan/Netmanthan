import { Chart } from "netmanthan-charts/dist/netmanthan-charts.esm";

netmanthan.provide("netmanthan.ui");
netmanthan.Chart = Chart;

netmanthan.ui.RealtimeChart = class RealtimeChart extends netmanthan.Chart {
	constructor(element, socketEvent, maxLabelPoints = 8, data) {
		super(element, data);
		if (data.data.datasets[0].values.length > maxLabelPoints) {
			netmanthan.throw(
				__(
					"Length of passed data array is greater than value of maximum allowed label points!"
				)
			);
		}
		this.currentSize = data.data.datasets[0].values.length;
		this.socketEvent = socketEvent;
		this.maxLabelPoints = maxLabelPoints;

		this.start_updating = function () {
			netmanthan.realtime.on(this.socketEvent, (data) => {
				this.update_chart(data.label, data.points);
			});
		};

		this.stop_updating = function () {
			netmanthan.realtime.off(this.socketEvent);
		};

		this.update_chart = function (label, data) {
			if (this.currentSize >= this.maxLabelPoints) {
				this.removeDataPoint(0);
			} else {
				this.currentSize++;
			}
			this.addDataPoint(label, data);
		};
	}
};
