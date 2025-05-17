/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ChartRenderer } from "./chart_renderer";
const { Component, onWillStart, useRef, useState } = owl;

export class OwlPropertyDashboard extends Component {
    static template = "property_dashboard.OwlPropertyDashboard";
    static components = { ChartRenderer };

    setup() {
        const today = new Date();
        const defaultStartDate = new Date(today);
        defaultStartDate.setDate(today.getDate() - 30);
        
        this.state = useState({
            start_date: defaultStartDate.toISOString().split("T")[0],
            end_date: today.toISOString().split("T")[0],
            property_data: { labels: [], datasets: [], total: 0 },
            site_data: { labels: [], datasets: [], total: 0 }, // Add total for Sites
            sold_properties: 0,
            sold_properties_data: { labels: [], datasets: [] }, // New state for sold properties bar chart
            revenue_data: { labels: [], datasets: [] },
            commission_data: { labels: [], datasets: [] },
            renderKey: 0,
        });

        this.startDateRef = useRef("startDate");
        this.endDateRef = useRef("endDate");
        this.orm = this.env.services.orm;

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async onFilterChange() {
        const startDate = this.startDateRef.el.value;
        const endDate = this.endDateRef.el.value;

        if (startDate && endDate && new Date(startDate) <= new Date(endDate)) {
            this.state.start_date = startDate;
            this.state.end_date = endDate;
            await this.loadData();
            this.state.renderKey += 1;
        } else {
            console.warn("Invalid date range: Start date must be before or equal to end date");
        }
    }

    async loadData() {
        const { start_date, end_date } = this.state;
        let domain = [
            ["create_date", ">=", start_date],
            ["create_date", "<=", end_date],
        ];

        // Property Data (Bar Chart: Total Properties by State)
        const totalProperties = await this.orm.searchCount("property.property", domain);
        const availableProperties = await this.orm.searchCount("property.property", [...domain, ["state", "=", "available"]]);
        const reservedProperties = await this.orm.searchCount("property.property", [...domain, ["state", "=", "reserved"]]);
        const soldProperties = await this.orm.searchCount("property.property", [...domain, ["state", "=", "sold"]]);
        const rentedProperties = await this.orm.searchCount("property.property", [...domain, ["state", "=", "rented"]]);
        const pendingSalesProperties = await this.orm.searchCount("property.property", [...domain, ["state", "=", "pending_sales"]]);

        const propertyData = {
            labels: ["Available", "Reserved","Pending Sales","Rented", "Sold"],
            datasets: totalProperties ? [{
                label: "Properties",
                data: [availableProperties, reservedProperties, pendingSalesProperties,rentedProperties,soldProperties],
                backgroundColor: ["#36A2EB", "#FFCE56", "#FF6384"],
                barThickness: 40,
            }] : [],
            total: totalProperties,
        };

        console.log("Property Data:", propertyData); // Debug log

        // Sites Data (Bar Chart: Properties per Site)
        let siteData = { labels: [], datasets: [], total: 0 };
        try {
            const sites = await this.orm.searchRead("property.site", [], ["id", "name"]);
            console.log("####################### all site", sites);
            const propertiesBySite = await this.orm.readGroup(
                "property.property",
                domain,
                ["site:count"],
                ["site"]
            );
            console.log("############ property by site", propertiesBySite);

            const siteMap = new Map(sites.map(site => [site.id, site.name]));
            console.log("############### sitemap", siteMap);
            const siteNames = sites.map(site => site.name);
            console.log("############# sitmap value", siteNames);

            const siteCounts = sites.map(site => {
                const siteProp = propertiesBySite.find(
                    prop => prop.site_id && prop.site_id[0] === site.id
                );
                console.log("testing ############################", siteProp);

                return {
                    site_name: site.name || "Unknown",
                    count: siteProp ? siteProp.site_id_count : 0,
                };
            });
        

            siteData = {
                labels: siteCounts.map(s => s.site_name),
                datasets: siteCounts.some(s => s.count >= 0) ? [{
                    label: "Properties",
                    data: siteCounts.map(s => s.count),
                    backgroundColor: "#4BC0C0",
                    barThickness: 40,
                }] : [],
                total: siteCounts.reduce((sum, s) => sum + s.count, 0),
            };
        } catch (error) {
            console.error("Error fetching site data:", error);
        }
        console.log("Site Data:", siteData); // Debug log

        // Sold Properties Data (Bar Chart: Sold Properties by State)
       // Sold Properties Data (Bar Chart: Sold Properties by State)
       const soldPropertiesCount = await this.orm.searchCount("property.sale", domain);
       const soldByState = await this.orm.readGroup(
           "property.sale",
           domain,
           ["state"],
           ["state"]
       );
       console.log("Sold Properties by State:", soldByState);

       // Define possible states to ensure all are included, even if count is 0
       const possibleStates = ["draft", "request_for_confirm", "confirm", "cancel"];
       const stateLabelsMap = {
        draft: "Ongoing",
        request_for_confirm: "Requested For Complete",
        confirm: "Complete",
        cancel: "Cancel",
    };
       const stateCounts = possibleStates.map(state => {
           const stateData = soldByState.find(item => item.state === state);
           return {
               state: stateLabelsMap[state],
               count: stateData ? stateData.state_count : 0,
           };
       });

       const soldPropertiesData = {
           labels: stateCounts.map(item => item.state),
           datasets: stateCounts.some(item => item.count > 0) ? [{
               label: "Sold Properties",
               data: stateCounts.map(item => item.count),
               backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
               barThickness: 40,
           }] : [],
       };
       console.log("Sold Properties Data:", soldPropertiesData);
        

        console.log("#################### soldPropertiesData ############",soldPropertiesData)

        // Revenue Data (Pie Chart: Total, Paid, Remaining from property.sale)
        let totalRevenue = 0, paidRevenue = 0, remainingRevenue = 0;
        try {
            const paymentLines = await this.orm.searchRead(
                "property.payment.line",
                [["sale_id.create_date", ">=", start_date], ["sale_id.create_date", "<=", end_date]],
                ["expected_amount", "paid_amount", "remaining"]
            );
            console.log("Payment Lines:", paymentLines); // Debug log
            totalRevenue = paymentLines.reduce((sum, line) => sum + (line.expected_amount || 0), 0);
            paidRevenue = paymentLines.reduce((sum, line) => sum + (line.paid_amount || 0), 0);
            remainingRevenue = paymentLines.reduce((sum, line) => sum + (line.remaining || 0), 0);
        } catch (error) {
            console.error("Error fetching payment lines:", error);
        }

        const revenueData = {
            labels: ["Total", "Paid", "Remaining"],
            datasets: totalRevenue || paidRevenue || remainingRevenue ? [{
                label: "Revenue",
                data: [totalRevenue, paidRevenue, remainingRevenue],
                backgroundColor: ["#36A2EB", "#FFCE56", "#FF6384"],
                barThickness: 40,
            }] : [],
        };

        console.log("Revenue Data:", revenueData); // Debug log

        // Commission Data (Bar Chart: Total, Paid, Remaining from property.sale)
        let totalCommission = 0, paidCommission = 0, remainingCommission = 0;
        try {
            const commissionLines = await this.orm.searchRead(
                "property.commission.line",
                [["sale_id.create_date", ">=", start_date], ["sale_id.create_date", "<=", end_date]],
                ["expected_amount", "paid_amount", "remaining"]
            );
            console.log("Commission Lines:", commissionLines); // Debug log
            totalCommission = commissionLines.reduce((sum, line) => sum + (line.expected_amount || 0), 0);
            paidCommission = commissionLines.reduce((sum, line) => sum + (line.paid_amount || 0), 0);
            remainingCommission = commissionLines.reduce((sum, line) => sum + (line.remaining || 0), 0);
        } catch (error) {
            console.error("Error fetching commission lines:", error);
        }

        const commissionData = {
            labels: ["Total", "Paid", "Remaining"],
            datasets: totalCommission || paidCommission || remainingCommission ? [{
                label: "Commission",
                data: [totalCommission, paidCommission, remainingCommission],
                backgroundColor: ["#36A2EB", "#FFCE56", "#FF6384"],

                barThickness: 40,
            }] : [],
        };

        console.log("Commission Data:", commissionData); // Debug log

        // Update state
        console.log("aaaaaaaaaaaaaaaaaaaaaaaaaaaa ############################", siteData.labels.length);

        Object.assign(this.state, {
            property_data: propertyData,
            sold_properties: soldPropertiesCount,
            sold_properties_data: soldPropertiesData, // Add new sold properties data
            revenue_data: revenueData,
            commission_data: commissionData,
        });
    }

    async onChartClick({ chartType, label, title }) {
        const { start_date, end_date } = this.state;
        let domain = [
            ["create_date", ">=", start_date],
            ["create_date", "<=", end_date],
        ];

        if (chartType === "bar" && title === "Property Status") {
            const statusMap = { Available: "available", Reserved: "reserved", Sold: "sold" };
            if (statusMap[label]) {
                domain.push(["state", "=", statusMap[label]]);
                this.env.services.action.doAction({
                    type: "ir.actions.act_window",
                    name: `Properties - ${label}`,
                    res_model: "property.property",
                    views: [[false, "list"], [false, "form"]],
                    domain: domain,
                    target: "current",
                });
            }
        
        } else if (chartType === "bar" && title === "Sold Properties") {
            const stateMap = { "draft": "draft", "sent": "sent", "sale": "sale", "done": "done", "cancel": "cancel" };
            if (stateMap[label]) {
                domain.push(["state", "=", stateMap[label]]);
                this.env.services.action.doAction({
                    type: "ir.actions.act_window",
                    name: `Sold Properties - ${label}`,
                    res_model: "property.sale",
                    views: [[false, "list"], [false, "form"]],
                    domain: domain,
                    target: "current",
                });
            }
        }
    }

    async openRecords(ev) {
        const type = ev.target.dataset.type;
        if (!type) return;

        const { start_date, end_date } = this.state;
        let domain = [
            ["create_date", ">=", start_date],
            ["create_date", "<=", end_date],
        ];

        if (type === "totalProperties") {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Total Properties",
                res_model: "property.property",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            });
        } else if (type === "soldProperties") {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Sold Properties",
                res_model: "property.sale",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            });
        }
    }
}

registry.category("actions").add("owl.property_dashboard", OwlPropertyDashboard);