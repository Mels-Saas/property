/** @odoo-module **/

import { loadJS } from "@web/core/assets";
const { Component, onWillStart, useRef, onMounted, onPatched, onWillUnmount } = owl;

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
                    title: {
                        display: true,
                        text: this.props.title,
                    },
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const label = this.props.data.labels[index];
                        console.log("Chart clicked:", { chartType: this.props.type, label, title: this.props.title });
                        this.props.onChartClick({
                            chartType: this.props.type,
                            label,
                            title: this.props.title,
                            st: this.props.start_date,
                            ed: this.props.end_date,
                        });
                    }
                },
            },
        });
    }

    updateChart() {
        if (this.chartInstance) {
            this.chartInstance.data = this.props.data;
            this.chartInstance.update();
            console.log("Chart updated:", this.props.title, this.props.data);
        }
    }

    willUnmount() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
    }
}