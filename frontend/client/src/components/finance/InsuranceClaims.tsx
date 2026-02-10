import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Shield, Plus, FileText, Calendar, AlertTriangle, CheckCircle2, Clock, XCircle, IndianRupee, RefreshCw, Send, Trash2, Eye } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useField } from "@/context/FieldContext";

interface Claim {
    id: number;
    field_id: number;
    field_name: string;
    crop: string;
    damage_type: string;
    damage_type_display: string;
    damage_date: string;
    area_affected_acres: number;
    estimated_loss: number;
    claim_amount: number | null;
    status: string;
    status_display: string;
    submitted_at: string | null;
    created_at: string;
}

interface ClaimFormData {
    field_id: string;
    crop: string;
    damage_type: string;
    damage_date: string;
    area_affected_acres: string;
    damage_description: string;
    estimated_loss: string;
    policy_number: string;
    bank_account: string;
    ifsc_code: string;
}

interface ClaimsData {
    claims: Claim[];
    summary: {
        total_claims: number;
        pending_claims: number;
        approved_total: number;
    };
    damage_types: { value: string; label: string; icon: string }[];
    tips: { icon: string; text: string }[];
}

const INITIAL_FORM: ClaimFormData = {
    field_id: '',
    crop: '',
    damage_type: '',
    damage_date: new Date().toISOString().split('T')[0],
    area_affected_acres: '',
    damage_description: '',
    estimated_loss: '',
    policy_number: '',
    bank_account: '',
    ifsc_code: '',
};

export function InsuranceClaims() {
    const { fields, selectedField } = useField();
    const [data, setData] = useState<ClaimsData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showNewClaimDialog, setShowNewClaimDialog] = useState(false);
    const [formData, setFormData] = useState<ClaimFormData>(INITIAL_FORM);
    const [submitting, setSubmitting] = useState(false);

    const fetchClaims = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiFetch('/finance/insurance');
            setData(response as ClaimsData);
        } catch (err) {
            setError('Failed to load insurance claims');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClaims();
    }, []);

    useEffect(() => {
        if (selectedField) {
            setFormData(prev => ({
                ...prev,
                field_id: String(selectedField.id),
                crop: selectedField.cropType || '',
            }));
        }
    }, [selectedField]);

    const handleInputChange = (field: keyof ClaimFormData, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmitClaim = async () => {
        setSubmitting(true);
        try {
            await apiFetch('/finance/insurance', {
                method: 'POST',
                body: JSON.stringify({
                    field_id: parseInt(formData.field_id),
                    crop: formData.crop,
                    damage_type: formData.damage_type,
                    damage_date: formData.damage_date,
                    area_affected_acres: parseFloat(formData.area_affected_acres),
                    damage_description: formData.damage_description,
                    estimated_loss: parseFloat(formData.estimated_loss),
                    policy_number: formData.policy_number,
                    bank_account: formData.bank_account,
                    ifsc_code: formData.ifsc_code,
                }),
            });

            setShowNewClaimDialog(false);
            setFormData(INITIAL_FORM);
            fetchClaims();
        } catch (err) {
            console.error('Failed to submit claim:', err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleSubmitForReview = async (claimId: number) => {
        try {
            await apiFetch(`/finance/insurance/${claimId}`, {
                method: 'PATCH',
                body: JSON.stringify({ status: 'submitted' }),
            });
            fetchClaims();
        } catch (err) {
            console.error('Failed to submit claim:', err);
        }
    };

    const handleDeleteClaim = async (claimId: number) => {
        if (!confirm('Are you sure you want to delete this draft claim?')) return;

        try {
            await apiFetch(`/finance/insurance/${claimId}`, { method: 'DELETE' });
            fetchClaims();
        } catch (err) {
            console.error('Failed to delete claim:', err);
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'draft': return <FileText className="h-4 w-4 text-gray-500" />;
            case 'submitted': return <Clock className="h-4 w-4 text-blue-500" />;
            case 'under_review': return <Eye className="h-4 w-4 text-yellow-500" />;
            case 'approved': return <CheckCircle2 className="h-4 w-4 text-green-500" />;
            case 'rejected': return <XCircle className="h-4 w-4 text-red-500" />;
            case 'paid': return <IndianRupee className="h-4 w-4 text-green-600" />;
            default: return <FileText className="h-4 w-4" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'draft': return 'bg-gray-100 text-gray-700';
            case 'submitted': return 'bg-blue-100 text-blue-700';
            case 'under_review': return 'bg-yellow-100 text-yellow-700';
            case 'approved': return 'bg-green-100 text-green-700';
            case 'rejected': return 'bg-red-100 text-red-700';
            case 'paid': return 'bg-emerald-100 text-emerald-700';
            default: return 'bg-gray-100 text-gray-700';
        }
    };

    const formatCurrency = (amount: number) => `₹${amount.toLocaleString('en-IN')}`;

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Shield className="h-6 w-6 text-primary" />
                        Insurance Claims
                    </h1>
                    <p className="text-muted-foreground">Manage your PMFBY crop insurance claims</p>
                </div>

                <div className="flex gap-2">
                    <Button variant="outline" onClick={fetchClaims} disabled={loading}>
                        <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>

                    <Dialog open={showNewClaimDialog} onOpenChange={setShowNewClaimDialog}>
                        <DialogTrigger asChild>
                            <Button>
                                <Plus className="h-4 w-4 mr-2" />
                                New Claim
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
                            <DialogHeader>
                                <DialogTitle>File New Insurance Claim</DialogTitle>
                            </DialogHeader>

                            <div className="space-y-4 py-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Field</Label>
                                        <Select value={formData.field_id} onValueChange={(v) => handleInputChange('field_id', v)}>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select field" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {fields.map(field => (
                                                    <SelectItem key={field.id} value={String(field.id)}>{field.name}</SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div className="space-y-2">
                                        <Label>Crop</Label>
                                        <Input
                                            value={formData.crop}
                                            onChange={(e) => handleInputChange('crop', e.target.value)}
                                            placeholder="e.g. Rice"
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Damage Type</Label>
                                        <Select value={formData.damage_type} onValueChange={(v) => handleInputChange('damage_type', v)}>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select type" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {data?.damage_types.map(type => (
                                                    <SelectItem key={type.value} value={type.value}>
                                                        {type.icon} {type.label}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div className="space-y-2">
                                        <Label>Damage Date</Label>
                                        <Input
                                            type="date"
                                            value={formData.damage_date}
                                            onChange={(e) => handleInputChange('damage_date', e.target.value)}
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Area Affected (acres)</Label>
                                        <Input
                                            type="number"
                                            step="0.1"
                                            value={formData.area_affected_acres}
                                            onChange={(e) => handleInputChange('area_affected_acres', e.target.value)}
                                            placeholder="e.g. 2.5"
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label>Estimated Loss (₹)</Label>
                                        <Input
                                            type="number"
                                            value={formData.estimated_loss}
                                            onChange={(e) => handleInputChange('estimated_loss', e.target.value)}
                                            placeholder="e.g. 50000"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label>Description of Damage</Label>
                                    <Textarea
                                        value={formData.damage_description}
                                        onChange={(e) => handleInputChange('damage_description', e.target.value)}
                                        placeholder="Describe the damage in detail..."
                                        rows={3}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label>Policy Number (optional)</Label>
                                    <Input
                                        value={formData.policy_number}
                                        onChange={(e) => handleInputChange('policy_number', e.target.value)}
                                        placeholder="e.g. PMFBY/2026/12345"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Bank Account</Label>
                                        <Input
                                            value={formData.bank_account}
                                            onChange={(e) => handleInputChange('bank_account', e.target.value)}
                                            placeholder="Account number"
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label>IFSC Code</Label>
                                        <Input
                                            value={formData.ifsc_code}
                                            onChange={(e) => handleInputChange('ifsc_code', e.target.value)}
                                            placeholder="e.g. SBIN0001234"
                                        />
                                    </div>
                                </div>

                                <Button
                                    onClick={handleSubmitClaim}
                                    disabled={submitting || !formData.field_id || !formData.damage_type}
                                    className="w-full"
                                >
                                    {submitting ? 'Saving...' : 'Save Draft Claim'}
                                </Button>
                            </div>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            {/* Summary Stats */}
            {data && (
                <div className="grid grid-cols-3 gap-4">
                    <Card className="bg-gradient-to-br from-blue-50 to-blue-100">
                        <CardContent className="p-4 text-center">
                            <div className="text-3xl font-bold text-blue-700">{data.summary.total_claims}</div>
                            <div className="text-sm text-blue-600">Total Claims</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100">
                        <CardContent className="p-4 text-center">
                            <div className="text-3xl font-bold text-yellow-700">{data.summary.pending_claims}</div>
                            <div className="text-sm text-yellow-600">Pending</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-green-50 to-green-100">
                        <CardContent className="p-4 text-center">
                            <div className="text-3xl font-bold text-green-700">{formatCurrency(data.summary.approved_total)}</div>
                            <div className="text-sm text-green-600">Approved Amount</div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {error && (
                <Card className="border-red-200 bg-red-50">
                    <CardContent className="p-4 flex items-center gap-2 text-red-700">
                        <AlertTriangle className="h-5 w-5" />
                        {error}
                    </CardContent>
                </Card>
            )}

            {/* Claims List */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold">Your Claims</h2>

                {data?.claims.length === 0 ? (
                    <Card>
                        <CardContent className="p-8 text-center text-muted-foreground">
                            <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                            <p>No insurance claims yet.</p>
                            <p className="text-sm">Click "New Claim" to file your first insurance claim.</p>
                        </CardContent>
                    </Card>
                ) : (
                    data?.claims.map(claim => (
                        <Card key={claim.id} className="overflow-hidden">
                            <CardContent className="p-4">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Badge className={getStatusColor(claim.status)}>
                                                {getStatusIcon(claim.status)}
                                                <span className="ml-1">{claim.status_display}</span>
                                            </Badge>
                                            <span className="text-sm text-muted-foreground">
                                                Claim #{claim.id}
                                            </span>
                                        </div>

                                        <h3 className="font-semibold">
                                            {claim.crop} - {claim.damage_type_display}
                                        </h3>
                                        <p className="text-sm text-muted-foreground">
                                            Field: {claim.field_name} • {claim.area_affected_acres} acres affected
                                        </p>

                                        <div className="flex items-center gap-4 mt-2 text-sm">
                                            <span className="flex items-center gap-1">
                                                <Calendar className="h-3 w-3" />
                                                {new Date(claim.damage_date).toLocaleDateString()}
                                            </span>
                                            <span className="flex items-center gap-1 font-semibold">
                                                <IndianRupee className="h-3 w-3" />
                                                Est. Loss: {formatCurrency(claim.estimated_loss)}
                                            </span>
                                            {claim.claim_amount && (
                                                <span className="flex items-center gap-1 text-green-600 font-semibold">
                                                    Approved: {formatCurrency(claim.claim_amount)}
                                                </span>
                                            )}
                                        </div>
                                    </div>

                                    <div className="flex gap-2">
                                        {claim.status === 'draft' && (
                                            <>
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => handleSubmitForReview(claim.id)}
                                                >
                                                    <Send className="h-4 w-4 mr-1" />
                                                    Submit
                                                </Button>
                                                <Button
                                                    size="sm"
                                                    variant="ghost"
                                                    className="text-red-500 hover:text-red-700"
                                                    onClick={() => handleDeleteClaim(claim.id)}
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>

            {/* Tips */}
            {data?.tips && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">💡 Claim Tips</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        {data.tips.map((tip, i) => (
                            <div key={i} className="flex items-start gap-2 text-sm">
                                <span>{tip.icon}</span>
                                <span>{tip.text}</span>
                            </div>
                        ))}
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
