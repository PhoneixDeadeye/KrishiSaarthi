import React from 'react';
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Download, FileJson, FileType } from "lucide-react";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { logger } from "@/lib/logger";

export interface Column {
    header: string;
    accessorKey: string;
}

interface ExportButtonProps {
    data: Record<string, unknown>[];
    filename?: string;
    columns: Column[];
    title?: string;
}

export function ExportButton({ data, filename = "export", columns, title = "Report" }: ExportButtonProps) {

    const handleExportCSV = () => {
        if (!data || !data.length) return;

        // Header row
        const headerRow = columns.map(col => col.header).join(",");

        // Data rows
        const rows = data.map(row => {
            return columns.map(col => {
                const val = row[col.accessorKey];
                // Handle strings with commas by quoting
                const stringVal = String(val === undefined || val === null ? "" : val);
                return stringVal.includes(",") ? `"${stringVal}"` : stringVal;
            }).join(",");
        });

        const csvContent = [headerRow, ...rows].join("\n");

        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const link = document.createElement("a");
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", `${filename}.csv`);
            link.style.visibility = "hidden";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    const handleExportPDF = () => {
        if (!data || !data.length) return;

        try {
            const doc = new jsPDF();

            // Add title
            doc.setFontSize(18);
            doc.text(title, 14, 22);

            // Add date
            doc.setFontSize(11);
            doc.setTextColor(100);
            doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 30);

            const tableColumn = columns.map(col => col.header);
            const tableRows: string[][] = [];

            data.forEach(item => {
                const rowData = columns.map(col => String(item[col.accessorKey] ?? ""));
                tableRows.push(rowData);
            });

            autoTable(doc, {
                head: [tableColumn],
                body: tableRows,
                startY: 35,
                theme: 'grid',
                styles: { fontSize: 10 },
                headStyles: { fillColor: [41, 128, 185], textColor: 255 }
            });

            doc.save(`${filename}.pdf`);
        } catch (error) {
            logger.error("PDF Export failed:", error);
            alert("PDF generation failed. Please ensure all dependencies are installed.");
        }
    };

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" className="gap-2">
                    <Download className="h-4 w-4" />
                    Export
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleExportCSV} className="cursor-pointer">
                    <FileType className="mr-2 h-4 w-4" />
                    Export as CSV
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleExportPDF} className="cursor-pointer">
                    <FileJson className="mr-2 h-4 w-4" />
                    Export as PDF
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
