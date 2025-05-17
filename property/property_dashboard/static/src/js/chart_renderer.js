/** @odoo-module **/

import { loadJS } from "@web/core/assets";
const { Component, onWillStart, useRef, onMounted, onPatched } = owl;

export class ChartRenderer extends Component {
    static template = "owl.ChartRenderer";

    setup() {
        this.chartRef = useRef("chart");
        this.chartInstance = null;

        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js");
        });

        onMounted(() => this.renderChart());
        onPatched(() => this.updateChart());
    }

    renderChart() {
        if (!this.chartRef.el || !window.Chart) {
            console.warn("Chart not rendered: Canvas or Chart.js not available");
            return;
        }

        if (!this.props.data?.datasets?.length) {
            console.warn("No valid datasets provided for chart:", this.props.title, this.props.data);
            return;
        }

        const ctx = this.chartRef.el.getContext("2d");
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }
        this.chartInstance = new Chart(ctx, {
            type: this.props.type,
            data: this.props.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: this.props.type === "pie",
                        position: "top",
                    },
                    title: {
                        display: true,
                        text: this.props.title,
                    },
                },
                scales: this.props.type === "bar" ? {
                    y: { beginAtZero: true },
                } : {},
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const label = this.props.data.labels[index];
                        console.log("Chart clicked:", { chartType: this.props.type, label, title: this.props.title });
                        this.props.onChartClick({ chartType: this.props.type, label, title: this.props.title });
                    }
                },
            },
        });
        console.log("Chart rendered:", this.props.title, this.props.data);
    }

    updateChart() {
        if (this.chartInstance && this.props.data?.datasets?.length) {
            this.chartInstance.data = this.props.data;
            this.chartInstance.update();
            console.log("Chart updated:", this.props.title, this.props.data);
        } else if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
            console.warn("Chart destroyed due to invalid data:", this.props.title, this.props.data);
        }
    }

    willUnmount() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
    }
}